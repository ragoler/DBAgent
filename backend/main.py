# FastAPI Application setup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging

from backend.core.agent_manager import agent_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Database Agentic System API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str = "default_user"
    session_id: str = "default_session"
    message: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        return StreamingResponse(
            agent_manager.chat_stream(request.user_id, request.session_id, request.message),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount the frontend directory (last to avoid shadowing API routes)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
