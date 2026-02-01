import os
import logging
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from backend.agents.adk.schema import create_schema_agent
from backend.agents.adk.sql_sequence import create_sql_sequence_agent
from backend.core.tools.report_tools import generate_summary_report

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
    Creates the Root Router agent that delegates tasks to sub-agents.
    """
    return LlmAgent(
        model=model_name,
        name="RootRouter",
        description="Analyzes user intent and routes to specialized agents.",
        instruction=(
            "You are the orchestrator of a Database Agentic System. "
            "Your job is to understand the user's intent and delegate to the right tool or agent."
            "\n\nINTENTS:"
            "\n1. SCHEMA: Questions about table structures, columns, or 'what tables exist'."
            "\n2. DATA: Questions about specific records, counts, or searches (e.g., 'Find flight 123')."
            "\n3. SUMMARY: Requests for a high-level status or summary of the database."
            "\n\nDELEGATION RULES:"
            "\n- Use 'delegate_to_schema_explorer' for intent 1."
            "\n- Use 'delegate_to_sql_agent' for intent 2."
            "\n- Use 'generate_summary_report' for intent 3."
            "\n- If the query is just a greeting, respond normally and skip delegation."
        ),
        tools=[
            delegate_to_schema_explorer,
            delegate_to_sql_agent,
            generate_summary_report
        ]
    )
