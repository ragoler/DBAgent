import pytest
from backend.core.database import database_context_var, get_session
from sqlalchemy import text
import os

@pytest.mark.skipif(not os.path.exists("data/movies.db"), reason="Movies DB not initialized")
def test_movies_query():
    # Switch context to movies
    token = database_context_var.set("movies")
    try:
        session = get_session()
        # Run a query
        result = session.execute(text("SELECT count(*) FROM movies")).fetchone()
        count = result[0]
        print(f"Movies count: {count}")
        assert count > 0
        
        # Verify schema columns (some checks)
        # SQLAlchemy returns keys in result object
        result = session.execute(text("SELECT * FROM movies LIMIT 1"))
        keys = result.keys()
        
        # Check for expected columns (based on vega movies.json)
        # We sanitized keys in init_movies_db.py, so they should be lower_snake_case
        keys_lower = [k.lower() for k in keys]
        
        # Common columns in movies dataset
        possible_title_cols = ['title', 'movie_title', 'name']
        found_title = any(col in keys_lower for col in possible_title_cols)
        
        if not found_title:
             print(f"Available columns: {keys_lower}")
        
        assert found_title, f"Could not find title column. Columns: {keys_lower}"
        
    finally:
        database_context_var.reset(token)
