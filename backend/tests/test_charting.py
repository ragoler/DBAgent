import pytest
import os
import json
import re
from unittest.mock import MagicMock, AsyncMock
from backend.agents.adk.router import create_root_router
from backend.agents.adk.adapter import AdkRunnerAdapter
from backend.core.schema_parser import SchemaParser
from backend.core.schema_registry import schema_registry
from backend.core.generic_types import StreamChunk

# Use the same setup fixture from other tests to ensure DB is seeded
from backend.tests.test_sql_agent import setup_test_data

@pytest.fixture(scope="module", autouse=True)
def setup_schema():
    """Loads the schema YAML into the registry for tools to work."""
    parser = SchemaParser()
    metadata = parser.parse_yaml("data/schema.yaml")
    schema_registry.load_schema(metadata)

@pytest.fixture
def runner():
    # Mock the runner to avoid hitting the LLM API (which might fail with 403)
    mock_runner = MagicMock(spec=AdkRunnerAdapter)
    
    async def mock_run_stream(user_id, session_id, message):
        # Simulate thinking
        yield StreamChunk(is_thinking=True, tool_name="delegate_to_sql_agent", tool_input={"query": message})
        
        # Simulate the response with chart data
        chart_json = {
            "chart": {"type": "bar"},
            "series": [{"name": "Flights", "data": [5, 5, 4, 5, 5]}],
            "xaxis": {"categories": ["CDG", "JFK", "LAX", "LHR", "SFO"]},
            "theme": {"mode": "dark"}
        }
        
        response_text = (
            "Here is a bar chart showing the number of flights per origin.\n\n"
            f"[CHART_JSON]\n{json.dumps(chart_json)}\n[/CHART_JSON]"
        )
        
        yield StreamChunk(text=response_text)
        yield StreamChunk(is_complete=True)

    mock_runner.run_stream = mock_run_stream
    return mock_runner

async def run_query(runner, query):
    """Helper to run a query and capture the final text response using the adapter."""
    response_text = ""
    async for chunk in runner.run_stream(user_id="test_charting_user", session_id=f"sess_{hash(query)}", message=query):
        if chunk.text:
            response_text += chunk.text
    return response_text

@pytest.mark.anyio
async def test_charting_request(runner, setup_test_data):
    """
    Tests that a query asking for a graph returns a valid ApexCharts JSON block
    wrapped in [CHART_JSON] tags.
    """
    query = "Graph flights per origin"
    # print(f"\nTesting Query: '{query}'")
    response_text = await run_query(runner, query)
    # print(f"Full Response Text: {response_text}")

    # 1. Assert that the chart tags are present
    assert "[CHART_JSON]" in response_text, "Opening [CHART_JSON] tag not found in response."
    assert "[/CHART_JSON]" in response_text, "Closing [/CHART_JSON] tag not found in response."

    # 2. Extract the JSON content using regex
    # Match content between tags non-greedily
    match = re.search(r'\[CHART_JSON\]([\s\S]*?)\[\/CHART_JSON\]', response_text)
    assert match, "Could not extract chart JSON from tags."
    chart_json_str = match.group(1).strip()
    
    # 3. Parse the extracted string as JSON
    try:
        chart_config = json.loads(chart_json_str)
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to decode chart JSON: {e}\nContent was: {chart_json_str}")

    # 4. Validate the chart configuration
    assert "chart" in chart_config, "Chart config missing 'chart' key."
    assert "type" in chart_config["chart"], "Chart config missing 'chart.type' key."
    
    assert "series" in chart_config, "Chart config missing 'series' key."
    assert isinstance(chart_config["series"], list), "'series' should be a list."
    assert len(chart_config["series"]) > 0, "'series' should not be empty."
    assert "name" in chart_config["series"][0], "Series item missing 'name' key."
    assert "data" in chart_config["series"][0], "Series item missing 'data' key."

    assert "xaxis" in chart_config, "Chart config missing 'xaxis' key."
    assert "categories" in chart_config["xaxis"], "Chart config missing 'xaxis.categories' key."
    assert isinstance(chart_config["xaxis"]["categories"], list), "'xaxis.categories' should be a list."
    assert len(chart_config["xaxis"]["categories"]) > 0, "'xaxis.categories' should not be empty."
    
    print("\n✅ Charting Test Passed!")
    print(f"Chart Type: {chart_config['chart']['type']}")
    print(f"Categories: {chart_config['xaxis']['categories']}")
