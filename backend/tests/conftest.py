import pytest
import os
from backend.core.database import register_database, database_context_var

@pytest.fixture(scope="session", autouse=True)
def setup_databases():
    """
    Registers databases for the test session.
    """
    # Register the default test database
    # Assuming test execution from project root
    register_database("flights", "sqlite:///data/flights.db")
    
    # Register movies DB if it exists, otherwise use memory or skip
    if os.path.exists("data/movies.db"):
        register_database("movies", "sqlite:///data/movies.db")
    
    # Set default context to flights
    token = database_context_var.set("flights")
    yield
    database_context_var.reset(token)
