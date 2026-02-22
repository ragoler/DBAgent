# FastAPI Application setup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
import os
import yaml

from backend.core.agent_manager import agent_manager
from backend.core.telemetry import setup_telemetry, instrument_adk_agents

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Database Agentic System API")
setup_telemetry(app)
instrument_adk_agents()

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
    database_id: str = "flights"

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/databases")
async def list_databases():
    """Returns the list of available databases."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "data", "databases.yaml")
    
    print(f"DEBUG: resolving databases from {config_path}")
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                # Return only public info (hide schema path or connection string if sensitive, 
                # but for this internal tool it's likely fine to return name/id).
                # Let's filter to be safe/clean.
                dbs = []
                for db in config.get("databases", []):
                    dbs.append({
                        "id": db["id"],
                        "name": db["name"],
                        "type": db["type"]
                    })
                print(f"DEBUG: found {len(dbs)} databases")
                return dbs
        except Exception as e:
            logger.error(f"Error reading databases.yaml: {e}")
            raise HTTPException(status_code=500, detail="Configuration error")
    
    print("DEBUG: databases.yaml not found")
    return []

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        return StreamingResponse(
            agent_manager.chat_stream(request.user_id, request.session_id, request.message, request.database_id),
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
