import pytest
pytestmark = pytest.mark.unit

from backend.core.database import register_database, get_engine, database_context_var, _engines

def test_engine_switching():
    register_database("test_db1", "sqlite:///:memory:")
    register_database("test_db2", "sqlite:///:memory:")
    
    # Switch to DB1
    token1 = database_context_var.set("test_db1")
    try:
        engine1 = get_engine()
        assert engine1 is not None
    finally:
        database_context_var.reset(token1)
    
    # Switch to DB2
    token2 = database_context_var.set("test_db2")
    try:
        engine2 = get_engine()
        assert engine2 is not None
        assert engine1 is not engine2
    finally:
        database_context_var.reset(token2)

def test_context_isolation():
    """Ensure context variable is properly isolated/reset."""
    # Assuming conftest sets "flights"
    current = database_context_var.get()
    assert current == "flights"
