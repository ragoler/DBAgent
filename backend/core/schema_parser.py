import yaml
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ColumnMetadata(BaseModel):
    name: str
    type: str
    primary_key: bool = False
    foreign_key: Optional[str] = None
    description: Optional[str] = None

class TableMetadata(BaseModel):
    name: str
    description: Optional[str] = None
    columns: List[ColumnMetadata]

class SchemaMetadata(BaseModel):
    tables: List[TableMetadata]

class SchemaParser:
    @staticmethod
    def parse_yaml(file_path: str) -> SchemaMetadata:
        """Parses a schema YAML file into Pydantic models."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return SchemaMetadata(**data)
