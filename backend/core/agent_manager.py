import os
import logging
from typing import AsyncGenerator
from dotenv import load_dotenv

from backend.core.schema_parser import SchemaParser
from backend.core.schema_registry import schema_registry
from backend.agents.adk.router import create_root_router
from backend.agents.adk.adapter import AdkRunnerAdapter

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
        
        # 1. Initialize Schema Registry
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schema_path = os.path.join(base_dir, "data", "schema.yaml")
        if os.path.exists(schema_path):
            metadata = SchemaParser.parse_yaml(schema_path)
            schema_registry.load_schema(metadata)
        
        # 2. Initialize the platform-specific implementation
        # For now, we hardcode ADK. In the future, this could be a factory.
        self.orchestrator = create_root_router(self.model_name)
        self.runner = AdkRunnerAdapter(agent=self.orchestrator, app_name=self.app_name)

    async def chat_stream(self, user_id: str, session_id: str, message: str) -> AsyncGenerator[str, None]:
        """
        Streams responses from the runner back to the UI.
        """
        async for chunk in self.runner.run_stream(user_id=user_id, session_id=session_id, message=message):
            if chunk.text:
                yield chunk.text
            elif chunk.is_thinking:
                logger.info(f"Agent is calling tool: {chunk.tool_name}")
                yield f"*(Thinking: examining {chunk.tool_name}...)* "
            
            if chunk.is_complete:
                logger.info("Chat turn complete.")

# Singleton instance
agent_manager = AgentManager()
