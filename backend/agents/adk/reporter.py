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
            "\nYou will receive raw data as a list of tuples, like `[('JFK', 10), ('LHR', 5)]`."
            "\n\n--- STRICT FORMATTING RULES ---"
            "\n1. **TABLE**: For 3 or more records, you MUST use a Markdown table."
            "\n2. **LIST**: For 1 or 2 records, use a bulleted list. Include all key-value pairs."
            "\n   - Example: * **Origin:** LHR, **Destination:** CDG"
            "\n3. **PROSE**: For single values (like a single count or name), respond in clean prose."
            "\n4. **NO DATA**: If the data is empty, respond with a polite message stating no results were found (e.g., 'Sorry, I couldn't find any results for that.')."
            "\n5. **CHART**: If the user asks for a 'graph', 'chart', or 'visualization', you MUST provide a prose summary AND an ApexCharts JSON config block."
            "\n\n--- CHART FORMATTING ---"
            "\n- To ensure readability on a dark UI, you MUST include a `theme` object set to dark mode: `\"theme\": {\"mode\": \"dark\"}`."
            "\n- When creating a chart from data like `[('JFK', 10), ('LHR', 5)]`:\n"
            "  - The first element of each tuple is the X-AXIS label (e.g., 'JFK', 'LHR'). This goes into `xaxis.categories`.\n"
            "  - The second element of each tuple is the Y-AXIS value (e.g., 10, 5). This goes into `series[0].data`.\n"
            "- You MUST wrap the ApexCharts JSON configuration between [CHART_JSON] and [/CHART_JSON] tags."
            "\n- It is CRITICAL that you use these exact tags. DO NOT use Markdown code fences (```json)."
            "\n- **EXAMPLE OF A GOOD RESPONSE (Given RAW DATABASE DATA: `[('JFK', 10), ('LHR', 5)]`)**:\n"
            "Here is a bar chart showing the number of flights per origin."
            "\n[CHART_JSON]"
            "\n{\"chart\": {\"type\": \"bar\"}, \"series\": [{\"name\": \"Flights\", \"data\": [10, 5]}], \"xaxis\": {\"categories\": [\"JFK\", \"LHR\"]}, \"theme\": {\"mode\": \"dark\"}}"
            "\n[/CHART_JSON]"
            "\n\n--- STYLE GUIDELINES ---"
            "\n- Be concise and polite. Do not mention the raw data or the query in your response."
            "\n- If the data has trends, mention them."
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
