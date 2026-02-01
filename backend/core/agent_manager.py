import os
import logging
from typing import AsyncGenerator
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

from backend.core.schema_parser import SchemaParser
from backend.core.schema_registry import schema_registry
from backend.agents.root_router_agent import create_root_router

load_dotenv()

logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self):
        self.app_name = "DBAgent"
        self.session_service = InMemorySessionService()
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        
        # Initialize the Schema Registry with sample data
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schema_path = os.path.join(base_dir, "data", "schema.yaml")
        if os.path.exists(schema_path):
            metadata = SchemaParser.parse_yaml(schema_path)
            schema_registry.load_schema(metadata)
        
        # Initialize the Root Router
        self.orchestrator = create_root_router(self.model_name)
        
        self.runner = Runner(
            agent=self.orchestrator,
            app_name=self.app_name,
            session_service=self.session_service,
            auto_create_session=True
        )

    async def chat_stream(self, user_id: str, session_id: str, message: str) -> AsyncGenerator[str, None]:
        user_content = types.Content(role='user', parts=[types.Part(text=message)])
        
        async for event in self.runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            # Log the event for debugging (safely)
            logger.info(f"Received event: {event}")
            
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        yield part.text
                    elif part.function_call:
                        # Log tool calls, but don't stream them to the UI directly for now
                        # unless we want to show 'Thinking...'
                        logger.info(f"Agent is calling tool: {part.function_call.name}")
                        yield f"*(Thinking: examining {part.function_call.name}...)* "

# Singleton instance
agent_manager = AgentManager()
