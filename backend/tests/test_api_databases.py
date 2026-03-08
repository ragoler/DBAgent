import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@pytest.mark.integration
def test_list_databases():
    response = client.get("/databases")
    assert response.status_code == 200
    dbs = response.json()
    assert isinstance(dbs, list)
    assert len(dbs) >= 1
    
    # Check if 'flights' is present
    flights = [db for db in dbs if db["id"] == "flights"]
    assert len(flights) == 1
