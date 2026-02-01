import os
import pytest
from backend.core.schema_parser import SchemaParser
from backend.core.schema_registry import schema_registry

def test_schema_parsing():
    """Verify that a valid schema YAML can be parsed into model objects."""
    schema_path = os.path.join(os.getcwd(), "data", "schema.yaml")
    assert os.path.exists(schema_path)
    
    metadata = SchemaParser.parse_yaml(schema_path)
    assert len(metadata.tables) > 0
    
    table_names = [t.name for t in metadata.tables]
    assert "pilots" in table_names
    assert "flights" in table_names

def test_schema_registry_lookup():
    """Verify that the registry correctly stores and retrieves metadata."""
    schema_path = os.path.join(os.getcwd(), "data", "schema.yaml")
    metadata = SchemaParser.parse_yaml(schema_path)
    
    schema_registry.load_schema(metadata)
    
    # Check table listing
    tables = schema_registry.get_table_names()
    assert "pilots" in tables
    
    # Check individual table details
    pilots = schema_registry.get_table("pilots")
    assert pilots is not None
    assert pilots.name == "pilots"
    assert len(pilots.columns) > 0
    
    # Check non-existent table
    bad = schema_registry.get_table("ghost_table")
    assert bad is None
