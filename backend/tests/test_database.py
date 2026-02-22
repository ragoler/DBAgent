from backend.core.database import get_session, get_engine, Base
from sqlalchemy import text

def test_db_connection():
    """Verify that we can connect to the database and create a session."""
    db = get_session()
    try:
        # Check if we can execute a simple query
        result = db.execute(text("SELECT 1")).fetchone()
        assert result[0] == 1
    finally:
        db.close()

def test_base_metadata():
    """Verify that our Base metadata is correctly initialized."""
    assert Base.metadata is not None
