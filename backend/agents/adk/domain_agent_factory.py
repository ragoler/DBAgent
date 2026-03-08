from typing import List
from google.adk.agents import SequentialAgent
from backend.core.schema_parser import TableMetadata
from backend.agents.adk.sql_sequence import create_sql_sequence_agent

def create_domain_agent(model_name: str, domain_name: str, tables: List[TableMetadata]) -> SequentialAgent:
    """
    Instantiates a specialized SequentialAgent restricted to the provided domain tables.
    """
    table_names = [t.name for t in tables]
    return create_sql_sequence_agent(model_name, domain_name=domain_name, table_names=table_names)
