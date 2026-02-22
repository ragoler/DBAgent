import logging
from typing import Any, Optional
from google.adk.agents import LlmAgent

logger = logging.getLogger(__name__)

def create_reporter_agent(model_name: str) -> LlmAgent:
    """
    Creates a specialized Reporting Agent for synthesizing raw data into narratives.
    """
    return LlmAgent(
        model=model_name,
        name="ReportingAgent",
        description="Synthesizes raw database results into natural language narratives.",
        instruction=(
            "You are a Reporting Specialist for the Database Agentic System. "
            "Your goal is to take raw database results and the original user query, "
            "and transform them into a final synthesized answer. "
            "\n\n--- DATA INPUT FORMAT ---"
            "\nYou will often receive raw data as a list of tuples, like `[('JFK', 10), ('LHR', 5)]`."
            "\n\n--- FORMATTING RULES ---"
            "\n1. **CHART**: If the user asks for a 'graph', 'chart', or 'visualization', you MUST provide a prose summary AND an ApexCharts JSON config block. "
            "Wrap the JSON in [CHART_JSON] and [/CHART_JSON] tags. Do not use markdown code fences."
            "\n2. **TABLE**: For non-chart queries with 3 or more records, use a Markdown table."
            "\n3. **LIST**: For non-chart queries with 1 or 2 records, use a bulleted list. Include all key-value pairs from the data."
            "\n4. **PROSE**: For single values (like a single count), respond in clean prose."
            "\n5. **NO DATA**: If the data is empty, politely state that no results were found."
            "\n\n--- CHART CONSTRUCTION ---"
            "\n- **BAR/LINE/AREA**: "
            "  - The first element of each tuple is the X-AXIS label. This goes into `xaxis.categories`."
            "  - The second element is the value. This goes into `series[0].data`."
            "\n- **PIE/DONUT**: "
            "  - The first element of each tuple is the label. This goes into top-level `labels` (list of strings)."
            "  - The second element is the value. This goes into `series` (simple list of numbers, NOT objects)."
            "\n- **NULL HANDLING**: If a category label is null/None, replace it with the string 'Unknown'."
            "\n- To ensure readability on a dark UI, you MUST include a `theme` object set to dark mode: `\"theme\": {\"mode\": \"dark\"}`."
            "\n- **BAR CHART EXAMPLE (Given `[('JFK', 10), ('LHR', 5)]`)**:\n"
            "[CHART_JSON]"
            '\n{"chart": {"type": "bar"}, "series": [{"name": "Flights", "data": [10, 5]}], "xaxis": {"categories": ["JFK", "LHR"]}, "theme": {"mode": "dark"}}'
            "\n[/CHART_JSON]"
            "\n- **PIE CHART EXAMPLE (Given `[('Action', 40), ('Comedy', 20)]`)**:\n"
            "[CHART_JSON]"
            '\n{"chart": {"type": "pie"}, "series": [40, 20], "labels": ["Action", "Comedy"], "theme": {"mode": "dark"}}'
            "\n[/CHART_JSON]"
            "\n\n--- STYLE GUIDELINES ---"
            "\n- Be concise and polite. Do not mention the raw data or the query in your response."
        )
    )

async def synthesize_response(model_name: str, query: str, raw_data: Any) -> str:
    """
    Programmatic helper to run the Reporting Agent on a chunk of data.
    """
    reporter = create_reporter_agent(model_name)
    
    prompt = (
        f"USER QUERY: {query}\n"
        f"RAW DATABASE DATA: {raw_data}\n\n"
        "Please provide the final synthesized response following your reporting rules."
    )
    
    # We use reporter.run conceptually; in a high-level manager, we might orchestrate this differently.
    # For now, we integrate it into the Sequential flows.
    return prompt # Placeholder for orchestration logic
