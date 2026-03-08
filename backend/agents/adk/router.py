import os
import logging
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from opentelemetry import trace
from backend.agents.adk.schema import create_schema_agent
from backend.agents.adk.domain_agent_factory import create_domain_agent
from backend.core.tools.report_tools import generate_summary_report
from backend.core.tools.format_tools import ensure_chart_tags
from backend.core.schema_registry import schema_registry

logger = logging.getLogger(__name__)

async def run_sub_agent(agent_creator, query: str, app_name: str) -> str:
    """Helper to run ephemeral sub-agents"""
    tracer = trace.get_tracer(__name__)
    
    # Create a span for the sub-agent execution
    # Context should propagate automatically in async
    with tracer.start_as_current_span(f"SubAgent: {app_name}", attributes={"query": query}) as span:
        model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
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
            # Use dummy IDs for the internal session
            # Using run_async to preserve context
            async for event in runner.run_async(new_message=user_msg, user_id="router_delegate", session_id="ephemeral_session"):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
        except Exception as e:
            logger.error(f"Error in {app_name}: {e}")
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            return f"Error: {str(e)}"
            
        return ensure_chart_tags(response_text)

async def delegate_to_schema_explorer(query: str) -> str:
    """Delegates schema questions (e.g. 'list tables', 'columns') to the Schema Agent."""
    return await run_sub_agent(create_schema_agent, query, "SchemaExplorerSubRun")

def create_root_router(model_name: str) -> LlmAgent:
    """
    Creates the Root Router agent that dynamically discovers domains and creates explicit delegation tools for each.
    """
    tools = [
        delegate_to_schema_explorer,
        generate_summary_report
    ]
    
    delegation_rules = [
        "- Use `delegate_to_schema_explorer` for SCHEMA intent.",
        "- Use `generate_summary_report` for SUMMARY intent.",
        "- If the query is just a greeting, respond normally and skip delegation."
    ]
    
    domains = schema_registry.get_tables_by_domain()
    
    # If no domains are found, we'll create a fallback 'Global' domain tool
    if not domains:
        def make_fallback():
            async def delegate_to_global_sql_agent(query: str) -> str:
                """Delegates data retrieval questions to the global SQL Agent."""
                logger.info(f"RootRouter delegating to Global SqlAgent: {query}")
                def agent_creator(model):
                    return create_domain_agent(model, "Global", [])
                return await run_sub_agent(agent_creator, query, "GlobalSqlAgentSubRun")
            return delegate_to_global_sql_agent
            
        fallback_tool = make_fallback()
        tools.append(fallback_tool)
        delegation_rules.insert(1, f"- Use `{fallback_tool.__name__}` for DATA and VISUALIZATION intents.")
    else:
        # Dynamically create a tool for each domain
        for domain_name, tables in domains.items():
            def make_delegate(d_name, d_tables):
                async def domain_delegate(query: str) -> str:
                    logger.info(f"RootRouter delegating to {d_name} Domain Agent: {query}")
                    def agent_creator(model):
                        return create_domain_agent(model, d_name, d_tables)
                    return await run_sub_agent(agent_creator, query, f"{d_name.replace(' ', '').replace('&', '')}AgentSubRun")
                
                # Format names securely for Python functions
                safe_name = d_name.lower().replace(' & ', '_and_').replace(' ', '_')
                domain_delegate.__name__ = f"delegate_to_{safe_name}_agent"
                
                table_list = ", ".join([t.name for t in d_tables])
                domain_delegate.__doc__ = (
                    f"Delegates data retrieval and visualization requests related to the '{d_name}' domain. "
                    f"This domain contains the following tables: {table_list}. "
                    "Use this tool when the user's question requires data from these specific tables."
                )
                return domain_delegate
                
            delegate_func = make_delegate(domain_name, tables)
            tools.append(delegate_func)
            delegation_rules.insert(1, f"- Use `{delegate_func.__name__}` for DATA and VISUALIZATION intents related to {domain_name} (tables: {', '.join([t.name for t in tables])}).")
            
    instruction_text = (
        "You are the orchestrator of a Database Agentic System. "
        "Your job is to understand the user's intent and delegate to the right tool or agent."
        "\n\n--- INTENTS ---"
        "\n1. **SCHEMA**: Questions about table structures, columns, or 'what tables exist'."
        "\n2. **DATA**: Questions about specific records, counts, or searches (e.g., 'Find flight 123')."
        "\n3. **VISUALIZATION**: Requests to 'graph', 'chart', or 'plot' data."
        "\n4. **SUMMARY**: Requests for a high-level status or summary of the database."
        "\n\n--- DELEGATION RULES ---"
        "\n" + "\n".join(delegation_rules) +
        "\n\nCRITICAL: You must choose EXACTLY ONE domain delegate if the user is asking a data question. Look at the tables associated with each delegate to decide."
    )

    return LlmAgent(
        model=model_name,
        name="RootRouter",
        description="Analyzes user intent and routes to specialized dynamic domain agents.",
        instruction=instruction_text,
        tools=tools
    )
