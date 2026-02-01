const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const reasoningSteps = document.getElementById('reasoning-steps');
const clearBtn = document.getElementById('clear-btn');

const API_URL = '';

// --- Core UI Helpers ---

function appendMessage(role, content = '') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role} animate-fade-in`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? 'U' : 'O';

    const text = document.createElement('div');
    text.className = 'text';
    text.innerHTML = content;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(text);
    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;
    return text;
}

function addReasoningStep(tool, input) {
    // Clear empty state if it exists
    const emptyState = reasoningSteps.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const stepDiv = document.createElement('div');
    stepDiv.className = 'step';

    const title = document.createElement('h4');
    title.innerHTML = `<span>🛠️ Call: ${tool}</span> <small>${new Date().toLocaleTimeString()}</small>`;

    const body = document.createElement('pre');
    body.textContent = typeof input === 'string' ? input : JSON.stringify(input, null, 2);

    stepDiv.appendChild(title);
    stepDiv.appendChild(body);
    reasoningSteps.prepend(stepDiv); // Show newest first
}

function clearChat() {
    chatMessages.innerHTML = '';
    reasoningSteps.innerHTML = `
        <div class="empty-state">
            <i>🧠</i>
            <p>Agent reasoning steps will appear here in real-time...</p>
        </div>
    `;
    appendMessage('agent', 'Chat cleared. How can I help you?');
}

// --- Charting Logic ---

function tryRenderChart(container, text) {
    // Look for [CHART_JSON]{...}[/CHART_JSON] pattern
    const chartRegex = /\[CHART_JSON\]([\s\S]*?)\[\/CHART_JSON\]/g;
    let match;
    let newText = text;

    while ((match = chartRegex.exec(text)) !== null) {
        try {
            const chartConfig = JSON.parse(match[1]);
            const chartId = 'chart-' + Math.random().toString(36).substr(2, 9);

            // Create a placeholder in the text where the chart will live
            const placeholder = `<div id="${chartId}" class="chart-container"></div>`;
            newText = newText.replace(match[0], placeholder);

            // Render after a small delay to ensure DOM is ready
            setTimeout(() => {
                const chartElement = document.getElementById(chartId);
                if (chartElement) {
                    const chart = new ApexCharts(chartElement, chartConfig);
                    chart.render();
                }
            }, 100);
        } catch (e) {
            console.error("Failed to parse chart JSON:", e);
        }
    }
    return newText;
}

// --- Interaction Logic ---

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    userInput.value = '';
    appendMessage('user', text);

    const agentTextContainer = appendMessage('agent');
    let accumulatedText = '';

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) throw new Error('Network error');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));

                        if (data.thought) {
                            addReasoningStep(data.thought.tool, data.thought.input);
                        }

                        if (data.text) {
                            accumulatedText += data.text;

                            // Check for charts and parse markdown
                            let html = accumulatedText;
                            if (window.marked) {
                                html = marked.parse(html);
                            }

                            // Clean HTML but keep our chart placeholders
                            if (window.DOMPurify) {
                                html = DOMPurify.sanitize(html, { ADD_TAGS: ['div'], ADD_ATTR: ['id', 'class'] });
                            }

                            agentTextContainer.innerHTML = tryRenderChart(agentTextContainer, html);
                        }
                    } catch (e) {
                        console.error("Stream parse error:", e, line);
                    }
                }
            }
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    } catch (error) {
        console.error('Error:', error);
        agentTextContainer.innerHTML = '<span style="color:#f87171">Error: Connection lost or server failure.</span>';
    }
}

// --- Event Listeners ---

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
clearBtn.addEventListener('click', clearChat);
