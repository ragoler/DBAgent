import pytest
from backend.core.schema_parser import SchemaMetadata, TableMetadata, ColumnMetadata
from backend.core.schema_registry import schema_registry
from backend.core.database import database_context_var
from backend.agents.adk.router import create_root_router

def test_dynamic_router_tools():
    # Setup mock schema
    meta = SchemaMetadata(
        tables=[
            TableMetadata(name="users", domain="Users & Identity", columns=[ColumnMetadata(name="id", type="int")]),
            TableMetadata(name="payments", domain="Billing", columns=[ColumnMetadata(name="id", type="int")]),
        ]
    )
    schema_registry.load_schema("test_dynamic_db", meta)
    token = database_context_var.set("test_dynamic_db")
    
    try:
        # Create router
        router = create_root_router("gemini-1.5-flash")
        
        # Verify dynamic tools were attached
        tool_names = [t.__name__ for t in router.tools]
        assert "delegate_to_users_and_identity_agent" in tool_names
        assert "delegate_to_billing_agent" in tool_names
        assert "delegate_to_schema_explorer" in tool_names
        
        # Verify rules injected
        assert "delegate_to_users_and_identity_agent" in router.instruction
        assert "delegate_to_billing_agent" in router.instruction
        assert "tables: users" in router.instruction
        assert "tables: payments" in router.instruction
    finally:
        database_context_var.reset(token)
