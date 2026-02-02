import re
import json

def ensure_chart_tags(response_text: str) -> str:
    """
    Finds a JSON block (raw or in a markdown fence) and wraps it in
    [CHART_JSON] tags if it's not already wrapped. This makes the LLM's
    chart output reliable and deterministic.
    """
    # If tags are already present, do nothing.
    if "[CHART_JSON]" in response_text:
        return response_text

    # Pattern to find a JSON object, possibly wrapped in ```json ... ```
    pattern = re.compile(r'```json\s*(\{[\s\S]*?\})\s*```|(\{[\s\S]*?\})', re.DOTALL)
    match = pattern.search(response_text)

    if match:
        # The actual JSON content will be in group 1 if wrapped in markdown,
        # or group 2 if it's a raw JSON object.
        json_str = match.group(1) or match.group(2)
        
        try:
            # Validate if it's actually JSON before wrapping
            json.loads(json_str)
            tagged_block = f"\n[CHART_JSON]\n{json_str.strip()}\n[/CHART_JSON]\n"
            
            # Replace the original matched block (markdown fence or raw) with the tagged version
            return response_text.replace(match.group(0), tagged_block)
        except (json.JSONDecodeError, TypeError):
            # Not a valid JSON block, do nothing
            return response_text
            
    return response_text
