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
            "\n\nSTRICT FORMATTING RULES:"
            "\n1. TABLE: You MUST use a Markdown Table if the data has more than 3 records/rows. No exceptions."
            "\n2. LIST: Use a Bulleted List if there are 1, 2, or 3 records/rows."
            "\n3. PROSE: Use a single sentence or short paragraph for single scalar values (like 'Total: 5') or if data is missing."
            "\n\nSTYLE GUIDELINES:"
            "\n- Don't just list data. Briefly mention any obvious trends or anomalies."
            "\n- Be concise and polite. Avoid technical jargon like 'SQL', 'rows', or 'JSON'."
            "\n- If no data is found, politely inform the user (e.g., 'I couldn't find any results for that')."
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
