import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_streaming_content():
    """Verify that the chat endpoint actually streams content."""
    payload = {"message": "Hello, what can you do?", "user_id": "test_u1", "session_id": "test_s1"}
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    
    # TestClient aggregates StreamingResponse into response.text/content
    assert len(response.text) > 0
    print(f"\nAggregated content: {response.text}")

def test_chat_multiple_messages_same_session():
    """Verify that multiple messages can be sent in the same session and stored."""
    session_id = "persistent_session"
    user_id = "test_user_p"
    payload1 = {"message": "First message", "session_id": session_id, "user_id": user_id}
    payload2 = {"message": "Second message", "session_id": session_id, "user_id": user_id}
    
    resp1 = client.post("/chat", json=payload1)
    assert resp1.status_code == 200
    
    resp2 = client.post("/chat", json=payload2)
    assert resp2.status_code == 200
    assert len(resp2.text) > 0
    
    # Deep check: Verify session state in ADK
    from backend.core.agent_manager import agent_manager
    import asyncio
    
    async def get_session():
        return await agent_manager.session_service.get_session(
            app_name=agent_manager.app_name, 
            user_id=user_id, 
            session_id=session_id
        )
    
    # Use a new event loop to avoid warnings in sync context
    session = asyncio.run(get_session())
    
    assert session is not None
    # Verify that there are events in history (each turn produces multiple events)
    assert len(session.events) > 0
    print(f"\nTotal events in session: {len(session.events)}")
