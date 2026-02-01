import logging
from typing import Dict, Any
from sqlalchemy import text
from backend.core.database import get_engine

logger = logging.getLogger(__name__)

def generate_summary_report() -> Dict[str, Any]:
    """
    Scans all tables in the database and returns a summary of record counts.
    Useful for high-level status reports and dashboarding.
    """
    engine = get_engine()
    summary = {}
    
    try:
        with engine.connect() as conn:
            # 1. Get all tables
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result.fetchall()]
            
            # 2. Get counts for each table
            for table in tables:
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                summary[table] = count_result.scalar()
                
        return {
            "status": "success",
            "table_counts": summary,
            "total_tables": len(tables)
        }
    except Exception as e:
        logger.error(f"Error generating summary report: {e}")
        return {"status": "error", "message": str(e)}
