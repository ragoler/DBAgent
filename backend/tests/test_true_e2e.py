import pytest
import os
import requests
import json
import uuid

# Skip these tests unless --run-network-e2e is passed (or some appropriate CI flag)
# Since we want to use them in CI to test the *deployed* app, we'll read a URL from ENV or default to localhost
API_BASE_URL = os.environ.get("DB_AGENT_API_URL", "http://localhost:8080")

@pytest.mark.e2e
def test_network_health_check():
    """Verify that the application is up and accessible over the network."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Could not connect to {API_BASE_URL}. Ensure the application is running!")

@pytest.mark.e2e
def test_network_chat_stream():
    """Verify that the /chat endpoint streams back a valid response over the network."""
    payload = {
        "message": "List the tables in the database.",
        "user_id": f"e2e_user_{uuid.uuid4().hex[:8]}",
        "session_id": f"e2e_session_{uuid.uuid4().hex[:8]}"
    }

    try:
        # Stream the response
        response = requests.post(f"{API_BASE_URL}/chat", json=payload, stream=True, timeout=30)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        received_text = ""
        has_thinking = False
        chunk_count = 0

        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if not decoded_line.startswith("data: "):
                    continue
                
                json_str = decoded_line[6:]
                try:
                    data = json.loads(json_str)
                    chunk_count += 1
                    
                    if "text" in data and data["text"]:
                        received_text += data["text"]
                    if "thought" in data:
                        has_thinking = True
                except json.JSONDecodeError:
                    continue

        assert chunk_count > 0, "No chunks received from the stream"
        assert len(received_text) > 0, "No text content returned from the model"
        # We don't assert 'has_thinking' strictly here because some queries might not trigger tools, 
        # but the connection works.

    except requests.exceptions.ConnectionError:
        pytest.fail(f"Could not connect to {API_BASE_URL}/chat. Ensure the application is running!")
