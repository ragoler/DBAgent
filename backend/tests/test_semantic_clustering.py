import pytest
from backend.core.schema_parser import TableMetadata, ColumnMetadata
from backend.core.semantic_clustering import SemanticClusterer

def create_mock_table(name: str, domain: str = None) -> TableMetadata:
    return TableMetadata(
        name=name,
        domain=domain,
        columns=[ColumnMetadata(name="id", type="int")]
    )

def test_semantic_clusterer_infers_domains():
    tables = [
        create_mock_table("users"),
        create_mock_table("invoices"),
        create_mock_table("products"),
        create_mock_table("audit_logs"),
        create_mock_table("flights"),
        create_mock_table("movies_metadata"),
        create_mock_table("sys_configuration"),
        create_mock_table("weird_unknown_table"),
        create_mock_table("already_set_table", domain="Custom Domain"),
    ]
    
    SemanticClusterer.cluster_tables(tables)
    
    # Check inferences
    assert tables[0].domain == "Users & Identity"
    assert tables[1].domain == "Billing & Sales"
    assert tables[2].domain == "Product Catalog"
    assert tables[3].domain == "Observability"
    assert tables[4].domain == "Travel & Operations"
    assert tables[5].domain == "Entertainment"
    assert tables[6].domain == "Sys"
    assert tables[7].domain == "Weird"
    
    # Check that already set domain is respected
    assert tables[8].domain == "Custom Domain"
