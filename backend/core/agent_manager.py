import os
import logging
import asyncio
import yaml
from typing import AsyncGenerator, Optional
from dotenv import load_dotenv
from backend.core import telemetry
from backend.core.schema_parser import SchemaParser
from backend.core.schema_registry import schema_registry
from backend.agents.adk.router import create_root_router
from backend.agents.adk.adapter import AdkRunnerAdapter
from backend.core.database import register_database, database_context_var

load_dotenv()

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Manages agent initialization and chat orchestration.
    Drives the UI by interacting with a BaseRunner.
    """
    def __init__(self):
        self.app_name = "DBAgent"
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        
        # 1. Initialize Databases and Schema Registry
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_config_path = os.path.join(base_dir, "data", "databases.yaml")
        
        if os.path.exists(db_config_path):
            with open(db_config_path, "r") as f:
                config = yaml.safe_load(f)
            
            for db in config.get("databases", []):
                db_id = db["id"]
                # Register Engine
                # Resolve relative path for sqlite
                conn_str = db["connection_string"]
                # If it's a file path in connection string, make it absolute if needed? 
                # SQLAlchemy usually handles it relative to CWD.
                register_database(db_id, conn_str)
                
                # Load Schema
                schema_file = os.path.join(base_dir, db["schema_file"])
                if os.path.exists(schema_file):
                    metadata = SchemaParser.parse_yaml(schema_file)
                    schema_registry.load_schema(db_id, metadata)
                else:
                    logger.warning(f"Schema file not found for database {db_id}: {schema_file}")
        else:
            logger.warning(f"Database configuration not found at {db_config_path}")
        
        # 2. Initialize the platform-specific implementation
        # For now, we hardcode ADK. In the future, this could be a factory.
        self.orchestrator = create_root_router(self.model_name)
        self.runner = AdkRunnerAdapter(agent=self.orchestrator, app_name=self.app_name)

    async def chat_stream(self, user_id: str, session_id: str, message: str, database_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Streams responses from the runner back to the UI.
        Yields JSON-encoded strings for structured handling in the frontend.
        """
        import json
        
        # Set the active database context for this request
        token = None
        if database_id:
             token = database_context_var.set(database_id)
        
        # Create a combined queue for agent output + telemetry
        queue = asyncio.Queue()
        
        # Register this queue to receive OTel spans
        telemetry.register_session_queue(session_id, queue)
        
        # Background task to push agent chunks to the queue
        async def run_agent():
            try:
                async for chunk in self.runner.run_stream(user_id=user_id, session_id=session_id, message=message):
                    await queue.put(chunk)
            except Exception as e:
                logger.error(f"Error in run_agent: {e}")
                await queue.put(e)
            finally:
                # Use None as sentinel for end of agent stream
                # BUT wait, telemetry might still be flushing?
                # Usually telemetry is synchronous or very fast after function return.
                # However, if we finish the agent stream, we are mostly done.
                await queue.put(None)

        task = asyncio.create_task(run_agent())
        
        try:
            while True:
                item = await queue.get()
                
                # End of stream sentinel
                if item is None:
                    # Check if task is actually done or failed
                    if task.done() and task.exception():
                        logger.error(f"Task failed: {task.exception()}")
                    break
                
                # Handle Errors
                if isinstance(item, Exception):
                    yield f"data: {json.dumps({'error': str(item)})}\n\n"
                    # We might want to continue or break? 
                    # Usually an error in runner is fatal for that turn.
                    break

                # Handle Telemetry Data (Dicts)
                if isinstance(item, dict):
                     yield f"data: {json.dumps({'trace': item})}\n\n"
                     continue

                # Handle Agent Stream Chunks
                # Assuming it's a StreamChunk object (has 'text', 'is_thinking', etc.)
                data = {}
                if hasattr(item, 'text') and item.text:
                    data["text"] = item.text
                if hasattr(item, 'is_thinking') and item.is_thinking:
                    # We still send this for legacy support, or maybe disable it?
                    # Let's keep it but mark it so frontend knows.
                    thought = {"tool": item.tool_name}
                    if hasattr(item, "tool_input") and item.tool_input:
                        thought["input"] = item.tool_input
                    data["thought"] = thought
                if hasattr(item, 'is_complete') and item.is_complete:
                    data["complete"] = True
                
                if data:
                    yield f"data: {json.dumps(data)}\n\n"
                    
        finally:
            telemetry.unregister_session_queue(session_id)
            if not task.done():
                task.cancel()
            if token:
                database_context_var.reset(token)

# Singleton instance
agent_manager = AgentManager()
