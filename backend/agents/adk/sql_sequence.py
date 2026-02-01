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
        instruction=(
            "You are a SQL writing expert. Your job is to write a single, valid SQLite query based on the user's question and the provided schema. "
            "\n\n--- QUERY PATTERNS ---"
            "\n1. **AGGREGATION/COUNTING**: If the user asks 'how many', 'count', 'graph', 'chart', or 'plot', you MUST use aggregation. This typically involves `COUNT(*)` and `GROUP BY`."
            "\n   - Example for 'graph flights per origin': `SELECT origin, COUNT(*) AS flight_count FROM flights GROUP BY origin`"
            "\n2. **SPECIFIC LOOKUP**: If the user asks for a specific item (e.g., 'flight 123', 'pilot named Maverick'), use a `WHERE` clause."
            "\n   - Example for 'flight with id 5': `SELECT * FROM flights WHERE id = 5`"
            "\n3. **GENERAL LISTING**: For general requests ('show all flights'), select a few relevant columns. Do not use `*`."
            "\n   - Example for 'list all pilots': `SELECT id, name, license_type FROM pilots`"
            "\n\n--- VALIDATION ---"
            "\nBefore finishing, you MUST call the `validate_sql` tool on your generated query. "
            "If validation fails, you MUST correct the query and call `validate_sql` again. "
            "Your final output must be ONLY the validated SQL query."
        ),
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
