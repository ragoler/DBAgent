import logging
import sqlparse
from sqlalchemy import text
from backend.core.database import get_session

logger = logging.getLogger(__name__)

# Security: Block mutable keywords for this Read-Only milestone
FORBIDDEN_KEYWORDS = {"DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "GRANT", "REVOKE"}

def validate_sql(query: str) -> str:
    """
    Validates a SQL query for syntax and prohibited keywords.
    Returns "VALID" if safe, or an error message if invalid/unsafe.
    """
    try:
        parsed = sqlparse.parse(query)
        if not parsed:
            return "Error: No SQL statement found."
        
        # Iterate through tokens to check for forbidden keywords
        # logic: flat list of tokens, check normalized value
        for statement in parsed:
            for token in statement.flatten():
                if token.ttype == sqlparse.tokens.Keyword.DML or token.ttype == sqlparse.tokens.Keyword.DDL:
                     if token.value.upper() in FORBIDDEN_KEYWORDS:
                         return f"Error: Mutable operation '{token.value.upper()}' is not allowed in Read-Only mode."
                # Also check raw value just in case parser misses DML type for some dialects
                if token.value.upper() in FORBIDDEN_KEYWORDS:
                     return f"Error: Forbidden keyword '{token.value.upper()}' detected."

        return "VALID"
    except Exception as e:
        logger.error(f"SQL validation error: {e}")
        return f"Error: The SQL query provided is invalid or contains syntax errors. Details: {str(e)}"

def execute_sql(query: str) -> str:
    """
    Executes a READ-ONLY SQL query against the database.
    Args:
        query: The SQL query to execute.
    Returns:
        A string representation of the results (Markdown table or list), or an error message.
    """
    # 1. Validate first
    validation = validate_sql(query)
    if validation != "VALID":
        return validation

    # 2. Execute
    session = get_session()
    try:
        # verify connection active
        result = session.execute(text(query))
        
        # 3. Format Results
        # Retrieve keys (column names)
        keys = result.keys()
        rows = result.fetchall()
        
        if not rows:
            return "Query executed successfully but returned no results."
            
        # Return as a simple dictionary or formatted string
        # Limit to 50 rows to prevent context window overflow
        limited_rows = rows[:50]
        data = [dict(zip(keys, row)) for row in limited_rows]
        
        output = f"Returned {len(limited_rows)} rows"
        if len(rows) > 50:
            output += " (truncated from total)."
        output += ":\n" + str(data)
        return output

    except Exception as e:
        logger.error(f"SQL Execution failed: {e}")
        return f"Database Error: {str(e)}"
    finally:
        session.close()
