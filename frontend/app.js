const expandAllBtn = document.getElementById('expand-all-btn');
const collapseAllBtn = document.getElementById('collapse-all-btn');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const reasoningSteps = document.getElementById('reasoning-steps');
const clearBtn = document.getElementById('clear-btn');
const databaseSelect = document.getElementById('database-select');

const API_URL = ''; // Relative path for same-origin
const traceMap = new Map();

// --- Initialization ---

async function fetchDatabases() {
    console.log("Fetching databases...");
    try {
        const response = await fetch(`${API_URL}/databases`);
        console.log("Database fetch response status:", response.status);
        
        if (!response.ok) throw new Error(`Failed to fetch databases: ${response.status} ${response.statusText}`);
        
        const databases = await response.json();
        console.log("Databases loaded:", databases);
        
        databaseSelect.innerHTML = '';
        databases.forEach(db => {
            const option = document.createElement('option');
            option.value = db.id;
            option.textContent = db.name;
            databaseSelect.appendChild(option);
        });
        
        // Select first one by default if available
        if (databases.length > 0) {
            databaseSelect.value = databases[0].id;
        } else {
             databaseSelect.innerHTML = '<option disabled>No databases found</option>';
        }
    } catch (e) {
        console.error("Error loading databases:", e);
        databaseSelect.innerHTML = '<option disabled>Error loading databases</option>';
    }
}

function initApp() {
    console.log("App initializing...");
    fetchDatabases();
    
    // --- Navigation Logic ---
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const text = item.querySelector('span').textContent.trim();
            
            // Remove active class from all
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            
            if (text === 'Database') {
                // Focus and try to open the selector
                if (databaseSelect) {
                    databaseSelect.focus();
                    // Click simulation for better UX (might not work in all browsers due to security)
                    try {
                        databaseSelect.click();
                    } catch (e) {
                        // Ignore click errors
                    }
                }
            }
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

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

function clearChat() {
    chatMessages.innerHTML = '';
    reasoningSteps.innerHTML = `
        <div class="empty-state">
            <i>🧠</i>
            <p>Agent reasoning steps will appear here in real-time...</p>
        </div>
    `;
    traceMap.clear();
    appendMessage('agent', 'Chat cleared. How can I help you?');
}

// --- Trace Visualization Logic ---

function handleTrace(trace) {
    // Remove empty state if present
    const emptyState = reasoningSteps.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const { event, data } = trace;
    const { span_id, parent_id, name, status, attributes } = data;

    if (event === 'start') {
        // Determine type (Agent or Tool)
        let type = 'unknown';
        let icon = '❓';
        let label = name;

        if (name.startsWith('Agent:')) {
            type = 'agent';
            icon = '🤖';
            label = name.replace('Agent: ', '');
        } else if (name.startsWith('Tool:')) {
            type = 'tool';
            icon = '🛠️';
            label = name.replace('Tool: ', '');
        } else if (name.startsWith('SubAgent:')) {
            type = 'subagent';
            icon = '🔄';
            label = name.replace('SubAgent: ', '');
        } else {
            type = 'generic';
            icon = '⚡';
        }

        // Create tree item using details/summary for proper nesting
        const details = document.createElement('details');
        details.id = `trace-${span_id}`;
        details.className = `trace-node ${type}`;
        details.open = true; // Auto-expand by default

        const summary = document.createElement('summary');
        summary.className = 'trace-header';
        
        // Tooltip
        const startTime = new Date(data.start_time / 1000000).toLocaleTimeString(); // approx
        let tooltip = `Name: ${name}\nStart: ${startTime}\nID: ${span_id.substring(0,8)}...`;
        if (attributes) {
             const attrKeys = Object.keys(attributes).filter(k => k !== 'query' && k !== 'tool_input');
             if (attrKeys.length > 0) {
                 tooltip += '\nAttributes:\n' + attrKeys.map(k => `- ${k}: ${attributes[k]}`).join('\n');
             }
        }
        summary.setAttribute('data-tooltip', tooltip);
        
        const labelSpan = document.createElement('span');
        labelSpan.className = 'trace-label';
        labelSpan.innerHTML = `${icon} <strong>${label}</strong>`;
        
        const statusSpan = document.createElement('span');
        statusSpan.className = 'trace-status running';
        statusSpan.textContent = '...'; 
        
        summary.appendChild(labelSpan);
        summary.appendChild(statusSpan);
        details.appendChild(summary);

        // Content container
        const contentDiv = document.createElement('div');
        contentDiv.className = 'trace-content';
        
        // Show inputs if available
        if (attributes && (attributes.query || attributes.tool_input)) {
            const inputPre = document.createElement('div');
            inputPre.className = 'trace-input';
            let inputContent = attributes.query || attributes.tool_input;
            if (typeof inputContent === 'object') {
                inputContent = JSON.stringify(inputContent, null, 2);
            }
            inputPre.textContent = `Input: ${inputContent}`;
            contentDiv.appendChild(inputPre);
        }
        
        details.appendChild(contentDiv);

        // Container for child nodes
        const childrenDiv = document.createElement('div');
        childrenDiv.id = `children-${span_id}`;
        childrenDiv.className = 'trace-children';
        details.appendChild(childrenDiv);

        // Append to parent or root
        if (parent_id && traceMap.has(parent_id)) {
            const parentChildrenContainer = document.getElementById(`children-${parent_id}`);
            if (parentChildrenContainer) {
                parentChildrenContainer.appendChild(details);
            } else {
                reasoningSteps.appendChild(details); // Fallback
            }
        } else {
            reasoningSteps.appendChild(details);
        }
        
        traceMap.set(span_id, details);
        reasoningSteps.scrollTop = reasoningSteps.scrollHeight;

    } else if (event === 'end') {
        const details = document.getElementById(`trace-${span_id}`);
        if (details) {
            const statusSpan = details.querySelector('.trace-status');
            const summary = details.querySelector('summary');
            
            if (statusSpan) {
                if (status === 'ERROR') {
                    statusSpan.className = 'trace-status error';
                    statusSpan.textContent = 'FAILED';
                    summary.classList.add('status-error');
                } else {
                    statusSpan.className = 'trace-status done';
                    statusSpan.textContent = 'DONE';
                    statusSpan.innerHTML = '✓';
                    summary.classList.add('status-success');
                }
            }
            // Update tooltip with status
            let currentTooltip = summary.getAttribute('data-tooltip') || '';
            currentTooltip += `\nStatus: ${status}`;
            summary.setAttribute('data-tooltip', currentTooltip);
        }
    }
}

// --- Tree Controls ---

if (expandAllBtn) {
    expandAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.trace-node').forEach(el => el.open = true);
    });
}

if (collapseAllBtn) {
    collapseAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.trace-node').forEach(el => el.open = false);
    });
}

// --- Charting Logic ---

function tryRenderChart(container, text) {
    // Look for [CHART_JSON]{...}[/CHART_JSON] pattern
    const chartRegex = /\[CHART_JSON\]([\s\S]*?)\[\/CHART_JSON\]/g;
    let match;
    let newText = text;

    while ((match = chartRegex.exec(text)) !== null) {
        const jsonStr = match[1];
        console.log("Found chart JSON match:", jsonStr);
        let chartConfig;
        
        try {
            chartConfig = JSON.parse(jsonStr);
            console.log("Parsed chart config:", chartConfig);
        } catch (e) {
            console.error("Failed to parse chart JSON:", e);
            // Fallback: Try to fix common LLM JSON errors (like over-escaping)
            try {
                // Replace \" with " and then retry
                const fixedStr = jsonStr.replace(/\\"/g, '"');
                chartConfig = JSON.parse(fixedStr);
                console.log("Parsed chart config after fix:", chartConfig);
            } catch (e2) {
                console.error("Failed to parse chart JSON even after fix:", e, e2);
                continue; // Skip this chart
            }
        }

        // Sanitize Config
        if (chartConfig.xaxis && Array.isArray(chartConfig.xaxis.categories)) {
            chartConfig.xaxis.categories = chartConfig.xaxis.categories.map(c => c === null ? "Unknown" : c);
        }
        if (Array.isArray(chartConfig.labels)) {
            chartConfig.labels = chartConfig.labels.map(l => l === null ? "Unknown" : l);
        }

        try {
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
                    console.log("Chart rendered to", chartId);
                } else {
                    console.error("Chart element not found:", chartId);
                }
            }, 100);
        } catch (e) {
            console.error("Error rendering chart:", e);
        }
    }
    return newText;
}

// --- Interaction Logic ---

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    const databaseId = databaseSelect.value;
    if (!databaseId) {
        alert("Please select a database first.");
        return;
    }

    userInput.value = '';
    appendMessage('user', text);

    const agentTextContainer = appendMessage('agent');
    let accumulatedText = '';

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: text,
                database_id: databaseId
            })
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

                        if (data.trace) {
                            handleTrace(data.trace);
                        }

                        // We rely on traces for reasoning now.
                        // data.thought is ignored.

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
