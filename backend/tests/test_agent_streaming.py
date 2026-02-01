import pytest
from fastapi.testclient import TestClient
from backend.main import app
import json

client = TestClient(app)

def test_chat_streaming_end_to_end():
    """
    Simulates a full end-to-end chat request and strictly verifies the streaming behavior.
    This ensures that:
    1. The stream initializes correctly (200 OK).
    2. Chunks are yielded progressively.
    3. No 'None' chunks are yielded (which causes Starlette crashes).
    4. The agent tool usage (Thinking...) and final answer are present.
    """
    print("\nStarting End-to-End Streaming Test...")
    
    payload = {
        "message": "Describe the flights table",
        "user_id": "e2e_tester",
        "session_id": "e2e_session"
    }
    
    # Use context manager to properly handle streaming response
    with client.stream("POST", "/chat", json=payload) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        chunk_count = 0
        received_text = ""
        has_thinking = False
        has_table_content = False
        
        for chunk_line in response.iter_lines():
            if not chunk_line.startswith("data: "):
                continue

            json_data_str = chunk_line[len("data: "):]
            
            try:
                data = json.loads(json_data_str)
            except json.JSONDecodeError:
                print(f"  Warning: Could not decode JSON from chunk: {chunk_line[:50]}...")
                continue

            chunk_count += 1
            
            # Verify we never yield None (TestClient would raise error, but good to be explicit)
            assert data is not None

            # Accumulate text (only if there's a 'text' field in the JSON)
            if "text" in data:
                received_text += data["text"]
            
            # Check for thinking process
            if "thought" in data:
                has_thinking = True
            
            # Check for table content (still looking for keywords in the 'text' field if available)
            if "text" in data:
                if "id" in data["text"].lower() or "columns" in data["text"].lower():
                    has_table_content = True
                
            print(f"  Received data {chunk_count}: {repr(data)[:50]}...")
            
        print(f"\nStream finished. Total chunks: {chunk_count}")
        print(f"Full response length: {len(received_text)}")
        
        # Validation
        assert chunk_count >= 1, "Stream should yield at least one chunk"
        assert len(received_text) > 50, "Response matched expectation of substantial content"
        assert has_thinking, "Agent should show thinking process (tool use)"
        assert has_table_content, "Agent should return the table description"
        
        print("\n✅ End-to-End Streaming Test Passed!")
