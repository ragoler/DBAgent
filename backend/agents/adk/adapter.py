import logging
import warnings
from typing import AsyncGenerator, Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from opentelemetry import trace

from backend.core.base_interfaces import BaseRunner
from backend.core.generic_types import StreamChunk
from backend.core.telemetry import session_context_var

# Suppress ADK deprecation warnings (moved from main.py)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google.adk")

logger = logging.getLogger(__name__)

class AdkRunnerAdapter(BaseRunner):
    """
    Implementation of BaseRunner using Google ADK.
    This file is the ONLY place (per architecture rule) that references ADK/GenAI.
    """
    def __init__(self, agent: Any, app_name: str):
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=agent,
            app_name=app_name,
            session_service=self.session_service,
            auto_create_session=True
        )

    async def run_stream(
        self, 
        user_id: str, 
        session_id: str, 
        message: str
    ) -> AsyncGenerator[StreamChunk, None]:
        # Set session context for telemetry
        token = session_context_var.set(session_id)
        tracer = trace.get_tracer(__name__)
        
        try:
            with tracer.start_as_current_span("AdkRunnerAdapter.run_stream", attributes={"user_id": user_id, "session_id": session_id}) as span:
                user_content = types.Content(role='user', parts=[types.Part(text=message)])
                
                async for event in self.runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
                    # Log the event for debugging
                    logger.debug(f"ADK Event: {event}")
                    
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                yield StreamChunk(text=part.text)
                            elif part.function_call:
                                # We can also create a span here if we want finer granularity, 
                                # but the tool execution itself should be instrumented.
                                yield StreamChunk(
                                    is_thinking=True, 
                                    tool_name=part.function_call.name,
                                    tool_input=part.function_call.args if hasattr(part.function_call, 'args') else None
                                )
                    
                    if event.turn_complete:
                        yield StreamChunk(is_complete=True)
        finally:
            session_context_var.reset(token)

    async def get_session(self, user_id: str, session_id: str) -> Any:
        return await self.session_service.get_session(
            app_name=self.runner.app_name,
            user_id=user_id,
            session_id=session_id
        )
