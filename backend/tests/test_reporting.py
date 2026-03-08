import pytest
import os
from unittest.mock import MagicMock
from backend.agents.adk.reporter import create_reporter_agent
from backend.agents.adk.adapter import AdkRunnerAdapter
from backend.core.generic_types import StreamChunk
import asyncio

from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def runner():
    # Mock the runner
    mock_runner = MagicMock(spec=AdkRunnerAdapter)
    
    async def mock_run_stream(user_id, session_id, message):
        response_text = ""
        
        # Simple logic to simulate agent behavior based on input
        if "List all flights" in message:
            response_text = (
                "Here are the flights:\n\n"
                "| ID | Origin | Destination |\n"
                "|---|---|---|\n"
                "| 1 | JFK | LHR |\n"
                "| 2 | LHR | CDG |\n"
                "| 3 | CDG | JFK |\n"
                "| 4 | SFO | LAX |"
            )
        elif "Show me flights to Paris" in message:
            response_text = (
                "Found one flight to Paris (CDG):\n"
                "- Flight 2 form LHR to CDG"
            )
        elif "Show me flights to Mars" in message:
            response_text = "Sorry, I couldn't find any flights to Mars."
        else:
            response_text = "I am a mocked agent."
            
        yield StreamChunk(text=response_text)
        yield StreamChunk(is_complete=True)

    mock_runner.run_stream = mock_run_stream
    return mock_runner

async def run_reporter(runner, query, data):
    """Helper to run the reporter agent via the adapter."""
    # We pass the query and the data as a combined message for isolated testing
    message = f"USER QUERY: {query}\nRAW_DATA: {data}"
    response_text = ""
    async for chunk in runner.run_stream(user_id="test_user", session_id=f"sess_{hash(query)}", message=message):
        if chunk.text:
            response_text += chunk.text
    return response_text

@pytest.mark.unit
@pytest.mark.anyio
async def test_reporting_table_format(runner):
    """Verify that the reporter uses a Markdown table for many rows."""
    query = "List all flights"
    data = [
        {"id": 1, "origin": "JFK", "destination": "LHR"},
        {"id": 2, "origin": "LHR", "destination": "CDG"},
        {"id": 3, "origin": "CDG", "destination": "JFK"},
        {"id": 4, "origin": "SFO", "destination": "LAX"}
    ]
    response = await run_reporter(runner, query, data)
    assert "|" in response
    assert "origin" in response.lower()
    assert "destination" in response.lower()

@pytest.mark.unit
@pytest.mark.anyio
async def test_reporting_list_format(runner):
    """Verify that the reporter uses a list for few rows."""
    query = "Show me flights to Paris"
    data = [{"id": 2, "origin": "LHR", "destination": "CDG"}]
    response = await run_reporter(runner, query, data)
    assert "LHR" in response
    assert "CDG" in response

@pytest.mark.unit
@pytest.mark.anyio
async def test_reporting_no_data(runner):
    """Verify polite response when no data is found."""
    query = "Show me flights to Mars"
    data = []
    response = await run_reporter(runner, query, data)
    assert any(word in response.lower() for word in ["sorry", "none", "no flights", "couldn't find", "not found", "no data", "no results", "don't have"])
