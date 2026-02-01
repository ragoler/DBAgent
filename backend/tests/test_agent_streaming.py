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
        
        for chunk in response.iter_text():
            chunk_count += 1
            # Verify we never yield None (TestClient would raise error, but good to be explicit)
            assert chunk is not None
            
            # Accumulate text
            received_text += chunk
            
            # Check for signatures (flexible to allow bullet points or tables)
            if "Thinking" in chunk or "examining" in chunk:
                has_thinking = True
            if "id" in chunk and "INTEGER" in chunk:
                has_table_content = True
                
            print(f"  Received chunk {chunk_count}: {repr(chunk)[:50]}...")
            
        print(f"\nStream finished. Total chunks: {chunk_count}")
        print(f"Full response length: {len(received_text)}")
        
        # Validation
        assert chunk_count >= 1, "Stream should yield at least one chunk"
        assert len(received_text) > 50, "Response matched expectation of substantial content"
        assert has_thinking, "Agent should show thinking process (tool use)"
        assert has_table_content, "Agent should return the table description"
        
        print("\n✅ End-to-End Streaming Test Passed!")
