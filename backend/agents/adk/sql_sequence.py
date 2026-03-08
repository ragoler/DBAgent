import logging
from typing import List, Any
from google.adk.agents import LlmAgent, SequentialAgent
from backend.core.tools.schema_tools import list_tables, describe_table
from backend.core.tools.sql_tools import execute_sql, validate_sql

from backend.agents.adk.reporter import create_reporter_agent

logger = logging.getLogger(__name__)

def create_sql_sequence_agent(model_name: str, domain_name: str = "General", table_names: List[str] = None) -> SequentialAgent:
    """
    Creates a Sequence Agent that follows a 4-step SQL generation workflow, scoped to a specific domain if provided.
    """
    
    domain_context = ""
    if table_names:
        domain_context = f"\nYou are the specialized agent for the '{domain_name}' domain. You only have access to the following tables: {', '.join(table_names)}. Do not attempt to query or gather information about other tables outside your domain.\n"
    
    # Step 1: Planner
    planner = LlmAgent(
        model=model_name,
        name=f"SqlPlanner_{domain_name.replace(' & ', '').replace(' ', '')}",
        description=f"Identifies required tables and columns for a query in the '{domain_name}' domain.",
        instruction=f"{domain_context}Review the user's question and use 'list_tables' and 'describe_table' to "
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
            "\n\n--- STRING ESCAPING ---"
            "\n- If a string value contains a single quote (e.g. \"Schindler's List\"), you MUST escape it by doubling the quote (e.g. 'Schindler''s List')."
            "\n- Do NOT use double quotes for string literals. Use single quotes only."
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
                    "Call 'execute_sql' EXACTLY ONCE with the provided query. "
                    "Output the result immediately. Do NOT retry. Do NOT fix the query. "
                    "If execution fails, output the error message as is."
                    "\n\nCRITICAL: Your final answer MUST be the raw output from the tool execution. "
                    "Do not summarize or explain it. Pass the data exactly as received.",
        tools=[execute_sql]
    )

    # Step 4: Narrator (Reporting Agent)
    narrator = create_reporter_agent(model_name)

    return SequentialAgent(
        name=f"SqlSequenceWorkflow_{domain_name.replace(' & ', '').replace(' ', '')}",
        sub_agents=[planner, generator, executor, narrator]
    )
