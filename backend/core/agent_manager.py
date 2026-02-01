import os
from typing import AsyncGenerator
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class AgentManager:
    def __init__(self):
        self.app_name = "DBAgent"
        self.session_service = InMemorySessionService()
        self.model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
        
        # Initialize the Dummy Orchestrator
        self.orchestrator = LlmAgent(
            model=self.model_name,
            name="Orchestrator",
            description="The primary entry point for user requests.",
            instruction="You are the lead orchestrator for a Database Agentic System. "
                        "For now, your job is to respond as a helpful assistant and acknowledge "
                        "that you will eventually route queries to specialized database agents."
        )
        
        self.runner = Runner(
            agent=self.orchestrator,
            app_name=self.app_name,
            session_service=self.session_service,
            auto_create_session=True
        )

    async def chat_stream(self, user_id: str, session_id: str, message: str) -> AsyncGenerator[str, None]:
        user_content = types.Content(role='user', parts=[types.Part(text=message)])
        
        async for event in self.runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if event.content and event.content.parts:
                yield event.content.parts[0].text

# Singleton instance
agent_manager = AgentManager()
