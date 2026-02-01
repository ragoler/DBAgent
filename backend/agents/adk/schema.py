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
                    "ALWAYS format your responses using clear Markdown (tables or bullet points).",
        tools=[list_tables, describe_table]
    )
