import logging
from typing import List
from backend.core.schema_parser import TableMetadata

logger = logging.getLogger(__name__)

class SemanticClusterer:
    """
    Utility class to group tables into semantic domains.
    If tables don't have an explicit 'domain' defined in their metadata, 
    this class will attempt to infer it using lightweight heuristics or groupings.
    """
    
    @staticmethod
    def cluster_tables(tables: List[TableMetadata]) -> None:
        """
        Modifies the tables in-place to assign a domain if one is missing.
        """
        for table in tables:
            if table.domain:
                continue
                
            inferred_domain = SemanticClusterer._infer_domain(table)
            table.domain = inferred_domain
            logger.debug(f"Assigned table '{table.name}' to domain '{inferred_domain}'")

    @staticmethod
    def _infer_domain(table: TableMetadata) -> str:
        """
        Basic heuristic to infer a domain. 
        In the future, this could be replaced with an LLM call or more complex graph analysis of foreign keys.
        """
        name_lower = table.name.lower()
        
        # Heuristics based on common table name patterns
        if any(keyword in name_lower for keyword in ["user", "account", "profile", "role", "permission", "tenant"]):
            return "Users & Identity"
        elif any(keyword in name_lower for keyword in ["order", "invoice", "payment", "billing", "subscription", "price", "cart"]):
            return "Billing & Sales"
        elif any(keyword in name_lower for keyword in ["product", "inventory", "catalog", "item", "category", "stock"]):
            return "Product Catalog"
        elif any(keyword in name_lower for keyword in ["log", "event", "audit", "trace", "metric"]):
            return "Observability"
        elif any(keyword in name_lower for keyword in ["flight", "booking", "passenger", "airport", "airline"]):
            return "Travel & Operations"
        elif any(keyword in name_lower for keyword in ["movie", "actor", "director", "genre", "review"]):
            return "Entertainment"
            
        # Fallback grouping based on table prefix (e.g., 'sys_config' -> 'Sys')
        parts = name_lower.split("_")
        if len(parts) > 1:
            return parts[0].capitalize()
            
        return "Core"
