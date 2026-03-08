from typing import List, Optional, Dict
from backend.core.schema_parser import SchemaMetadata, TableMetadata
from backend.core.database import database_context_var

class SchemaRegistry:
    _instance = None
    _schemas: Dict[str, SchemaMetadata] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchemaRegistry, cls).__new__(cls)
        return cls._instance

    def load_schema(self, db_id: str, metadata: SchemaMetadata):
        """Loads and stores the schema metadata for a specific database."""
        self._schemas[db_id] = metadata

    def get_tables(self, db_id: Optional[str] = None) -> List[TableMetadata]:
        """Returns all table definitions for the active database."""
        if db_id is None:
            db_id = database_context_var.get()
        
        # Fallback for single-DB setup or if only one schema is loaded
        if (not db_id or db_id not in self._schemas) and len(self._schemas) == 1:
            db_id = next(iter(self._schemas))

        if db_id and db_id in self._schemas:
            return self._schemas[db_id].tables
        return []

    def get_table_names(self, db_id: Optional[str] = None) -> List[str]:
        """Returns a list of all table names for the active database."""
        return [t.name for t in self.get_tables(db_id)]

    def get_table(self, table_name: str, db_id: Optional[str] = None) -> Optional[TableMetadata]:
        """Returns metadata for a specific table in the active database."""
        tables = self.get_tables(db_id)
        for table in tables:
            if table.name.lower() == table_name.lower():
                return table
        return None

# Global instance
schema_registry = SchemaRegistry()
