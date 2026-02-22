import pytest
from backend.core.schema_registry import schema_registry
from backend.core.schema_parser import SchemaMetadata, TableMetadata, ColumnMetadata
from backend.core.database import database_context_var

def test_multi_schema_storage():
    schema1 = SchemaMetadata(tables=[TableMetadata(name="t1", columns=[])])
    schema2 = SchemaMetadata(tables=[TableMetadata(name="t2", columns=[])])
    
    schema_registry.load_schema("db1", schema1)
    schema_registry.load_schema("db2", schema2)
    
    assert len(schema_registry.get_tables("db1")) == 1
    assert schema_registry.get_tables("db1")[0].name == "t1"
    
    assert len(schema_registry.get_tables("db2")) == 1
    assert schema_registry.get_tables("db2")[0].name == "t2"

def test_context_aware_retrieval():
    schema3 = SchemaMetadata(tables=[TableMetadata(name="t3", columns=[])])
    schema_registry.load_schema("db3", schema3)
    
    token = database_context_var.set("db3")
    try:
        tables = schema_registry.get_tables()
        assert len(tables) == 1
        assert tables[0].name == "t3"
    finally:
        database_context_var.reset(token)
