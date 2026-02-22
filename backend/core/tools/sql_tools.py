import logging
import sqlparse
from sqlalchemy import text
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from backend.core.database import get_session
from backend.core.telemetry import session_context_var

logger = logging.getLogger(__name__)

# Security: Block mutable keywords for this Read-Only milestone
FORBIDDEN_KEYWORDS = {"DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "GRANT", "REVOKE"}

def validate_sql(query: str) -> str:
    """
    Validates a SQL query for syntax and prohibited keywords.
    Returns "VALID" if safe, or an error message if invalid/unsafe.
    """
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("Tool: validate_sql", attributes={"query": query}) as span:
        try:
            # 1. Check for Prohibited Keywords (Static Analysis)
            parsed = sqlparse.parse(query)
            if not parsed:
                return "Error: No SQL statement found."
            
            for statement in parsed:
                for token in statement.flatten():
                    if token.ttype == sqlparse.tokens.Keyword.DML or token.ttype == sqlparse.tokens.Keyword.DDL:
                         if token.value.upper() in FORBIDDEN_KEYWORDS:
                             return f"Error: Mutable operation '{token.value.upper()}' is not allowed in Read-Only mode."
                    if token.value.upper() in FORBIDDEN_KEYWORDS:
                         return f"Error: Forbidden keyword '{token.value.upper()}' detected."

            # 2. Check Syntax using SQLite EXPLAIN (Dynamic Analysis)
            session = get_session()
            try:
                # Use EXPLAIN QUERY PLAN to validate syntax without executing
                session.execute(text(f"EXPLAIN QUERY PLAN {query}"))
                return "VALID"
            except Exception as db_err:
                return f"Syntax Error: {str(db_err)}"
            finally:
                session.close()

        except Exception as e:
            logger.error(f"SQL validation error: {e}")
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            return f"Error: Validation failed. {str(e)}"

def execute_sql(query: str) -> str:
    """
    Executes a READ-ONLY SQL query against the database.
    Args:
        query: The SQL query to execute.
    Returns:
        A string representation of the results (Markdown table or list), or an error message.
    """
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("Tool: execute_sql", attributes={"query": query}) as span:
        # 1. Validate first
        validation = validate_sql(query)
        if validation != "VALID":
            span.set_status(Status(StatusCode.ERROR, validation))
            return validation

        # 2. Execute
        session = get_session()
        try:
            print(f"\n--- EXECUTING SQL ---\n{query}\n---------------------\n")
            result = session.execute(text(query))
            
            # 3. Format Results
            keys = result.keys()
            rows = result.fetchall()
            
            if not rows:
                return "Query executed successfully but returned no results."
                
            # Return as a simple dictionary or formatted string
            limited_rows = rows[:50]
            data = [dict(zip(keys, row)) for row in limited_rows]
            
            output = f"Returned {len(limited_rows)} rows"
            if len(rows) > 50:
                output += " (truncated from total)."
            output += ":\n" + str(data)
            
            # Add result summary to span
            span.set_attribute("row_count", len(rows))
            
            return output

        except Exception as e:
            logger.error(f"SQL Execution failed: {e}")
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR))
            return f"Database Error: {str(e)}"
        finally:
            session.close()
