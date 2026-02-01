import logging
from typing import List, Any
from google.adk.agents import LlmAgent, SequentialAgent
from backend.core.tools.schema_tools import list_tables, describe_table
from backend.core.tools.sql_tools import execute_sql, validate_sql

from backend.agents.adk.reporter import create_reporter_agent

logger = logging.getLogger(__name__)

def create_sql_sequence_agent(model_name: str) -> SequentialAgent:
    """
    Creates a Sequence Agent that follows a 4-step SQL generation workflow.
    """
    
    # Step 1: Planner
    planner = LlmAgent(
        model=model_name,
        name="SqlPlanner",
        description="Identifies required tables and columns for a query.",
        instruction="Review the user's question and use 'list_tables' and 'describe_table' to "
                    "discover the necessary database structure. Your output should clearly list "
                    "the tables and columns needed for the query. IMPORTANT: If the user asks "
                    "for 'all flights' or general data, be sure to include descriptive columns "
                    "like 'destination', 'origin', 'name', etc., so the final answer is helpful.",
        tools=[list_tables, describe_table]
    )

    # Step 2: Generator & Validator
    generator = LlmAgent(
        model=model_name,
        name="SqlGenerator",
        description="Constructs and validates a SQLite query.",
        instruction="Use the schema information from the previous step to write a SQLite query. "
                    "You MUST call 'validate_sql' on your query before proceeding. "
                    "If validation fails, fix the query and try again. "
                    "Only output the final VALID SQL query.",
        tools=[validate_sql]
    )

    # Step 3: Executor
    executor = LlmAgent(
        model=model_name,
        name="SqlExecutor",
        description="Executes the validated SQL query.",
        instruction="Execute the SQL query provided by the previous step using 'execute_sql'. "
                    "Do not modify the query. If the execution returns an error, explain it.",
        tools=[execute_sql]
    )

    # Step 4: Narrator (Reporting Agent)
    narrator = create_reporter_agent(model_name)

    return SequentialAgent(
        name="SqlSequenceWorkflow",
        sub_agents=[planner, generator, executor, narrator]
    )
