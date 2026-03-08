import pytest
pytestmark = pytest.mark.unit

import json
import re
from backend.agents.adk.reporter import create_reporter_agent

# Mock the LLM output to simulate what we expect (since we can't invoke real LLM here easily)
# But we can check if the instructions contain the right directives.

def test_reporter_instructions_contain_chart_tags():
    """
    Verify that the ReportingAgent's instructions explicitly mention the custom chart tags.
    """
    agent = create_reporter_agent("test-model")
    instruction = agent.instruction
    
    assert "[CHART_JSON]" in instruction
    assert "[/CHART_JSON]" in instruction
    assert "Do not use markdown code fences" in instruction

def test_chart_tag_regex_matching():
    """
    Verify that the frontend's regex pattern correctly matches the expected output format.
    This duplicates the logic in frontend/app.js to ensure Python/JS parity.
    """
    # Simulate a valid response from the agent
    response_text = """
    Here is the chart you requested:
    [CHART_JSON]
    {
        "chart": {"type": "bar"},
        "series": [{"data": [10, 20]}]
    }
    [/CHART_JSON]
    Hope this helps!
    """
    
    # Regex from frontend/app.js: /\[CHART_JSON\]([\s\S]*?)\[\/CHART_JSON\]/g
    # In Python re.DOTALL is needed for [\s\S] equivalent or just . with DOTALL
    pattern = re.compile(r'\[CHART_JSON\]([\s\S]*?)\[\/CHART_JSON\]')
    
    match = pattern.search(response_text)
    assert match is not None
    
    json_str = match.group(1).strip()
    try:
        data = json.loads(json_str)
        assert data["chart"]["type"] == "bar"
        assert len(data["series"]) == 1
    except json.JSONDecodeError:
        pytest.fail("Failed to parse extracted JSON")

def test_chart_tag_regex_nested_json():
    """
    Verify that the regex handles nested JSON objects correctly.
    """
    response_text = """
    [CHART_JSON]
    {
        "chart": {
            "type": "bar",
            "toolbar": {
                "show": true
            }
        },
        "series": [
            {
                "name": "Series 1",
                "data": [1, 2, 3]
            }
        ]
    }
    [/CHART_JSON]
    """
    pattern = re.compile(r'\[CHART_JSON\]([\s\S]*?)\[\/CHART_JSON\]')
    match = pattern.search(response_text)
    assert match is not None
    
    json_str = match.group(1).strip()
    data = json.loads(json_str)
    assert data["chart"]["toolbar"]["show"] is True
