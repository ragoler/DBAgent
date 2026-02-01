import pytest
from backend.core.tools.sql_tools import validate_sql, execute_sql
from backend.core.database import get_engine, Base
from sqlalchemy import text

# --- Fixtures ---
@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    """Seeds the test database with some flight and pilot data."""
    engine = get_engine()
    with engine.connect() as conn:
        # Create Tables
        conn.execute(text("CREATE TABLE IF NOT EXISTS pilots (id INTEGER PRIMARY KEY, name VARCHAR, license_type VARCHAR)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS planes (id INTEGER PRIMARY KEY, model VARCHAR, capacity INTEGER)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS flights (id INTEGER PRIMARY KEY, pilot_id INTEGER, plane_id INTEGER, origin VARCHAR, destination VARCHAR, departure_time TIMESTAMP)"))
        
        # Clean Slate
        conn.execute(text("DELETE FROM flights"))
        conn.execute(text("DELETE FROM pilots"))
        conn.execute(text("DELETE FROM planes"))
        
        # Seed Data
        conn.execute(text("INSERT INTO pilots (id, name, license_type) VALUES (1, 'Maverick', 'Military'), (2, 'Amelia', 'Commercial'), (3, 'Charles', 'Private'), (4, 'Bessie', 'Commercial'), (5, 'Howard', 'Private')"))
        conn.execute(text("INSERT INTO planes (id, model, capacity) VALUES (1, 'Boeing 737', 150), (2, 'Airbus A320', 180), (3, 'Cessna 172', 4), (4, 'Gulfstream G650', 19), (5, 'Boeing 787', 250)"))
        
        # Original 2 flights for tests
        conn.execute(text("INSERT INTO flights (id, pilot_id, plane_id, origin, destination, departure_time) VALUES (1, 1, 1, 'JFK', 'LHR', '2023-11-01 10:00:00'), (2, 2, 1, 'LHR', 'CDG', '2023-11-01 15:30:00')"))
        
        # Add 18 more mock flights to satisfy user request and persistent state
        import random
        from datetime import datetime, timedelta
        airports = ['JFK', 'LHR', 'CDG', 'SFO', 'LAX']
        for i in range(3, 21):
            origin = random.choice(airports)
            dest = random.choice([a for a in airports if a != origin])
            conn.execute(text(
                "INSERT INTO flights (id, pilot_id, plane_id, origin, destination, departure_time) "
                "VALUES (:id, :p_id, :pl_id, :origin, :dest, '2023-11-15 12:00:00')"
            ), {"id": i, "p_id": random.randint(1, 5), "pl_id": random.randint(1, 5), "origin": origin, "dest": dest})
        
        conn.commit()
    yield

# --- Unit Tests for Tools ---

def test_validate_sql_safety():
    assert validate_sql("SELECT * FROM flights") == "VALID"
    assert "Error: Mutable operation" in validate_sql("DROP TABLE flights")
    assert "Error: Mutable operation" in validate_sql("DELETE FROM flights")
    assert "Error: Mutable operation" in validate_sql("INSERT INTO flights VALUES (3, 'Berlin')")

def test_execute_sql_success():
    result = execute_sql("SELECT destination FROM flights WHERE id = 1")
    assert "LHR" in result
    assert "Returned 1 rows" in result

def test_execute_sql_blocked():
    result = execute_sql("DELETE FROM flights WHERE id = 1")
    assert "Error: Mutable operation" in result

# --- Integration Tests for Agent (Mocked/Live) ---
# We rely on the generic E2E test in test_agent_streaming.py for full integration,
# but can add a specific router test here if needed.

