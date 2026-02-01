import os
import logging
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from backend.agents.schema_agent import create_schema_agent

logger = logging.getLogger(__name__)

def delegate_to_schema_explorer(query: str) -> str:
    """
    Delegates the user's query to the specialized Schema Explorer Agent.
    Use this when the user asks about tables, columns, schema, or database structure.
    
    Args:
        query: The user's question or command regarding the schema.
    """
    logger.info(f"RootRouter delegating to SchemaExplorer: {query}")
    
    # Initialize the sub-agent
    # TODO: In the future, we should cache this or use a shared Registry
    model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
    agent = create_schema_agent(model_name)
    
    # Run the sub-agent in a transient session
    # We use a new session service so it doesn't pollute the main chat history with tool steps,
    # but we lose context of previous sub-turns. For M3 token-efficiency, this is acceptable.
    runner = Runner(
        agent=agent,
        session_service=InMemorySessionService(),
        app_name="SchemaExplorerSubRun",
        auto_create_session=True
    )
    
    # Wrap query in a Content object as expected by ADK
    from google.genai import types
    user_msg = types.Content(role='user', parts=[types.Part(text=query)])
    
    response_text = ""
    
    # Run synchronously to return a simple string to the Router
    # Using dummy IDs for the ephemeral sub-session
    try:
        for event in runner.run(new_message=user_msg, user_id="router_delegate", session_id="ephemeral_session"):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
    except Exception as e:
        logger.error(f"Error in SchemaExplorer sub-run: {e}")
        return f"Error consulting Schema Explorer: {str(e)}"
        
    return response_text

def create_root_router(model_name: str) -> LlmAgent:
    """
    Creates the Root Router agent.
    """
    return LlmAgent(
        model=model_name,
        name="RootRouter",
        description="The central dispatcher that analyzes user intent.",
        instruction="You are the Root Router for the Database Agentic System. "
                    "Your goal is to understand the user's intent and route it to the correct specialized agent. "
                    "1. If the user asks about the database schema (e.g. 'list tables', 'columns in table X', 'do we have flights?'), "
                    "   you MUST call the tool 'delegate_to_schema_explorer'. "
                    "   Pass their exact query as the argument. "
                    "   Return the tool's output to the user. "
                    "2. If the user engages in general small talk (e.g. 'Hello', 'Who are you?'), answer directly. "
                    "Do NOT attempt to guess database table names yourself. You have no direct access to the database.",
        tools=[delegate_to_schema_explorer]
    )
