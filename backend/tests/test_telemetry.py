import pytest
from fastapi.testclient import TestClient
from backend.main import app
import json
from backend.core.schema_parser import SchemaParser
from backend.core.schema_registry import schema_registry

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_schema():
    """Loads the schema YAML into the registry for tools to work."""
    parser = SchemaParser()
    metadata = parser.parse_yaml("data/flight_schema.yaml")
    schema_registry.load_schema("flights", metadata)

def test_telemetry_streaming():
    """
    Verifies that the streaming response includes OpenTelemetry trace data.
    """
    payload = {
        "message": "Describe the flights table",
        "user_id": "telemetry_tester",
        "session_id": "telemetry_session"
    }
    
    with client.stream("POST", "/chat", json=payload) as response:
        assert response.status_code == 200
        
        has_trace = False
        trace_events = []
        
        for chunk_line in response.iter_lines():
            line = chunk_line.decode('utf-8') if isinstance(chunk_line, bytes) else chunk_line
            if not line.startswith("data: "):
                continue

            json_data_str = line[6:]
            try:
                data = json.loads(json_data_str)
                if "trace" in data:
                    has_trace = True
                    trace_events.append(data["trace"])
            except json.JSONDecodeError:
                continue
        
        assert has_trace, "Stream should include at least one trace event"
        # We expect at least one start and one end event (AdkRunnerAdapter.run_stream)
        assert len(trace_events) >= 2, "Stream should include start and end trace events"
        
        # Verify trace structure
        start_event = next((t for t in trace_events if t["event"] == "start"), None)
        assert start_event is not None
        assert "span_id" in start_event["data"]
        assert "name" in start_event["data"]
        assert start_event["data"]["name"] == "AdkRunnerAdapter.run_stream"
        
        # Verify session_id injection
        assert "session_id" in start_event["data"]["attributes"]
        assert start_event["data"]["attributes"]["session_id"] == "telemetry_session"

def test_tool_telemetry(setup_schema):
    """
    Verifies that direct tool calls generate OTel spans with correct attributes.
    """
    from unittest.mock import MagicMock, patch
    from backend.core.tools.schema_tools import list_tables
    from backend.core.tools.sql_tools import validate_sql
    from backend.core.telemetry import session_context_var
    
    # Mock the tracer and span
    mock_tracer = MagicMock()
    mock_span = MagicMock()
    
    # Context manager mock
    mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
    
    # Set context var
    token = session_context_var.set("tool_test_session")
    
    try:
        # Patch trace.get_tracer where it is imported in the tools
        # We need to patch 'opentelemetry.trace.get_tracer' generally or in the specific modules
        with patch('backend.core.tools.schema_tools.trace.get_tracer', return_value=mock_tracer) as mock_get_tracer_schema:
            list_tables()
            mock_tracer.start_as_current_span.assert_called_with("Tool: list_tables")
            # Verify attribute setting (table_count)
            # The tool uses trace.get_current_span().set_attribute
            # So we also need to mock trace.get_current_span
            pass

        with patch('backend.core.tools.sql_tools.trace.get_tracer', return_value=mock_tracer) as mock_get_tracer_sql:
            validate_sql("SELECT * FROM flights")
            mock_tracer.start_as_current_span.assert_called_with("Tool: validate_sql", attributes={"query": "SELECT * FROM flights"})
            
    finally:
        session_context_var.reset(token)

if __name__ == "__main__":
    test_telemetry_streaming()
