import os
import logging
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from backend.agents.adk.schema import create_schema_agent
from backend.agents.adk.sql_sequence import create_sql_sequence_agent

logger = logging.getLogger(__name__)

def run_sub_agent(agent_creator, query: str, app_name: str) -> str:
    """Helper to run ephemeral sub-agents"""
    model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")
    agent = agent_creator(model_name)
    
    runner = Runner(
        agent=agent,
        session_service=InMemorySessionService(),
        app_name=app_name,
        auto_create_session=True
    )
    
    from google.genai import types
    user_msg = types.Content(role='user', parts=[types.Part(text=query)])
    
    response_text = ""
    try:
        # Use dummy IDs
        for event in runner.run(new_message=user_msg, user_id="router_delegate", session_id="ephemeral_session"):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text
    except Exception as e:
        logger.error(f"Error in {app_name}: {e}")
        return f"Error: {str(e)}"
        
    return response_text

def delegate_to_schema_explorer(query: str) -> str:
    """Delegates schema questions (e.g. 'list tables', 'columns') to the Schema Agent."""
    return run_sub_agent(create_schema_agent, query, "SchemaExplorerSubRun")

def delegate_to_sql_agent(query: str) -> str:
    """
    Delegates data retrieval questions (e.g. 'how many users', 'find flight 123') to the SQL Agent.
    Use this when the user asks for ACTUAL DATA, not just table definitions.
    """
    logger.info(f"RootRouter delegating to SQLAgent: {query}")
    return run_sub_agent(create_sql_sequence_agent, query, "SqlAgentSubRun")

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
                    "1. SCHEMA QUERY: If asking about structure (tables, columns), call 'delegate_to_schema_explorer'. "
                    "2. DATA QUERY: If asking for actual data ('show me rows', 'count', 'who is'), call 'delegate_to_sql_agent'. "
                    "3. CHAT: If small talk, answer directly. "
                    "Do NOT run SQL yourself. Do NOT guess schema.",
        tools=[delegate_to_schema_explorer, delegate_to_sql_agent]
    )
