from google.adk.agents import LlmAgent
from backend.core.tools.schema_tools import list_tables, describe_table
from backend.core.tools.sql_tools import execute_sql

def create_sql_agent(model_name: str) -> LlmAgent:
    """
    Creates the SQL Generation Agent.
    This agent is responsible for translating natural language into SQL, executing it, and interpreting results.
    """
    return LlmAgent(
        model=model_name,
        name="SqlGenerator",
        description="Generates and executes SQL queries to retrieve data.",
        instruction="You are a SQL Expert for the Database Agentic System. Your task is to query the database to answer user questions. "
                    "THINK STEP-BY-STEP: "
                    "1. SEARCH: If you don't know the schema, call 'list_tables' and 'describe_table' immediately. "
                    "   NEVER ask the user for metadata (tables, columns). You have tools for this. "
                    "2. PREPARE: Write a SQLite query based on the tool results. "
                    "3. EXECUTE: Use 'execute_sql'. "
                    "4. VERIFY: If results are empty but you expected data, or if you got a SQL error, check your column names and retry once. "
                    "RESTRICTIONS: Read-Only. No DROP/DELETE/INSERT.",
        tools=[list_tables, describe_table, execute_sql]
    )
