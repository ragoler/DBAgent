import difflib
from typing import List, Dict, Any
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from backend.core.schema_registry import schema_registry

def list_tables() -> List[str]:
    """
    Returns a list of all available tables in the database.
    Use this to get an overview of the data structure.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("Tool: list_tables"):
        print("DEBUG: list_tables called")
        tables = schema_registry.get_table_names()
        # Add result to span
        trace.get_current_span().set_attribute("table_count", len(tables))
        return tables

def describe_table(table_name: str) -> Dict[str, Any]:
    """
    Returns the column definitions and descriptions for a specific table.
    
    Args:
        table_name: The name of the table to describe.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("Tool: describe_table", attributes={"table_name": table_name}) as span:
        print(f"DEBUG: describe_table called for '{table_name}'")
        table = schema_registry.get_table(table_name)
        if not table:
            # Fuzzy matching logic
            all_tables = schema_registry.get_table_names()
            close_matches = difflib.get_close_matches(table_name, all_tables, n=1, cutoff=0.6)
            
            error_msg = f"Table '{table_name}' not found."
            if close_matches:
                suggestion = close_matches[0]
                error_msg += f" Did you mean '{suggestion}'?"
            
            span.set_status(Status(StatusCode.ERROR, error_msg))
            return {"error": error_msg}
        
        return table.model_dump()
