from typing import List, Optional, Dict
from backend.core.schema_parser import SchemaMetadata, TableMetadata

class SchemaRegistry:
    _instance = None
    _metadata: Optional[SchemaMetadata] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchemaRegistry, cls).__new__(cls)
        return cls._instance

    def load_schema(self, metadata: SchemaMetadata):
        """Loads and stores the schema metadata."""
        self._metadata = metadata

    def get_tables(self) -> List[TableMetadata]:
        """Returns all table definitions."""
        return self._metadata.tables if self._metadata else []

    def get_table_names(self) -> List[str]:
        """Returns a list of all table names."""
        return [t.name for t in self.get_tables()]

    def get_table(self, table_name: str) -> Optional[TableMetadata]:
        """Returns metadata for a specific table."""
        if not self._metadata:
            return None
        for table in self._metadata.tables:
            if table.name.lower() == table_name.lower():
                return table
        return None

# Global instance
schema_registry = SchemaRegistry()
