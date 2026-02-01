import pytest
from backend.core.tools.schema_tools import describe_table, list_tables
from backend.core.schema_registry import schema_registry
from backend.core.schema_parser import SchemaMetadata, TableMetadata, ColumnMetadata

@pytest.fixture(autouse=True)
def setup_registry():
    # Setup a clean registry with known data for testing
    metadata = SchemaMetadata(tables=[
        TableMetadata(
            name="flights",
            description="Flights table",
            columns=[
                ColumnMetadata(name="id", type="INTEGER", description="Flight ID")
            ]
        ),
        TableMetadata(
            name="pilots",
            description="Pilots table",
            columns=[
                ColumnMetadata(name="id", type="INTEGER", description="Pilot ID")
            ]
        )
    ])
    schema_registry.load_schema(metadata)

def test_list_tables():
    tables = list_tables()
    assert "flights" in tables
    assert "pilots" in tables
    assert len(tables) == 2

def test_describe_table_exact_match():
    result = describe_table("flights")
    assert result["name"] == "flights"
    assert len(result["columns"]) == 1

def test_describe_table_not_found():
    result = describe_table("non_existent_table")
    assert "error" in result
    assert "not found" in result["error"]

def test_describe_table_fuzzy_match():
    # "flight" should match "flights"
    result = describe_table("flight")
    assert "error" in result
    assert "Did you mean 'flights'?" in result["error"]

    # "pilot" should match "pilots"
    result = describe_table("pilot")
    assert "error" in result
    assert "Did you mean 'pilots'?" in result["error"]
