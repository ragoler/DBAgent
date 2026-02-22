from google.adk.agents import LlmAgent
from backend.core.tools.schema_tools import list_tables, describe_table

def create_schema_agent(model_name: str) -> LlmAgent:
    """
    Creates the Schema Explorer Agent responsible for inspecting database metadata.
    """
    return LlmAgent(
        model=model_name,
        name="SchemaExplorer",
        description="Explores and describes the database schema (tables and columns).",
        instruction="You are a specialized agent for exploring the database schema. "
                    "Your job is to tell the user what data is available. "
                    "Use 'list_tables' to see available tables. "
                    "Use 'describe_table' to see columns in a specifically named table. "
                    "Do not hallucinate table names. "
                    "\n\nFORMATTING RULES:\n"
                    "1. When describing multiple tables, separate them with a horizontal rule (---).\n"
                    "2. Use '### Table: [Name]' for table headers.\n"
                    "3. Present column details (Name, Type, Description) in a Markdown table for better readability.\n"
                    "4. Include the table description as italicized text immediately under the header.\n\n"
                    "CRITICAL: You MUST include the actual data (table names, column details) in your response. Do not suppress the output.",
        tools=[list_tables, describe_table]
    )
