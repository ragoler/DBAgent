const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

const API_URL = ''; // Uses current origin

function appendMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role} animate-fade-in`;

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? 'U' : 'O';

    const text = document.createElement('div');
    text.className = 'text';
    text.textContent = content;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(text);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return text;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Clear input
    userInput.value = '';

    // Append user message
    appendMessage('user', text);

    // Create placeholder for agent response
    const agentText = appendMessage('agent', '...');
    agentText.textContent = ''; // Clear the dots

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) throw new Error('Network response was not ok');

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let accumulatedText = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            accumulatedText += chunk;

            // Render markdown safely if libraries are loaded
            if (window.marked && window.DOMPurify) {
                try {
                    const rawHtml = marked.parse(accumulatedText);
                    const cleanHtml = DOMPurify.sanitize(rawHtml);
                    agentText.innerHTML = cleanHtml;
                } catch (e) {
                    console.error("Markdown rendering failed:", e);
                    agentText.textContent = accumulatedText;
                }
            } else {
                // Fallback for when CDNs are blocked
                agentText.textContent = accumulatedText;
            }

            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    } catch (error) {
        console.error('Error:', error);
        agentText.textContent = 'Sorry, something went wrong. Please check if the backend is running.';
        agentText.style.color = '#f87171';
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
