import asyncio
import logging
from typing import Dict, Tuple, Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, ReadableSpan, Span
from opentelemetry.sdk.trace.export import SpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.context import Context
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# ContextVar to hold the current session_id for tools/sub-agents
session_context_var: ContextVar[Optional[str]] = ContextVar("session_id", default=None)

# Global registry: session_id -> (loop, queue)
_session_queues: Dict[str, Tuple[asyncio.AbstractEventLoop, asyncio.Queue]] = {}

class StreamSpanProcessor(SpanProcessor):
    """
    Custom SpanProcessor that pushes span start/end events to an asyncio Queue 
    for real-time frontend visualization.
    """
    def on_start(self, span: Span, parent_context: Optional[Context] = None):
        # Inject session_id from context if not present
        if not span.attributes or "session_id" not in span.attributes:
            current_session = session_context_var.get()
            if current_session:
                span.set_attribute("session_id", current_session)
        
        self._emit(span, "start")

    def on_end(self, span: ReadableSpan):
        self._emit(span, "end")

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis: int = 30000):
        return True

    def _emit(self, span: ReadableSpan, event_type: str):
        # Access attributes safely
        attributes = span.attributes or {}
        session_id = attributes.get("session_id")
        
        if session_id and session_id in _session_queues:
            loop, queue = _session_queues[session_id]
            formatted_span = self._format_span(span, event_type)
            
            if loop.is_running():
                loop.call_soon_threadsafe(queue.put_nowait, formatted_span)

    def _format_span(self, span: ReadableSpan, event_type: str):
        """Convert OTel span to a JSON-serializable dict."""
        parent_id = None
        if span.parent and span.parent.span_id:
             parent_id = f"{span.parent.span_id:016x}"
             
        # Convert attributes to basic types
        attrs = {}
        if span.attributes:
            for k, v in span.attributes.items():
                if isinstance(v, (str, int, float, bool)):
                    attrs[k] = v
                else:
                    attrs[k] = str(v)

        return {
            "type": "trace",
            "event": event_type,
            "data": {
                "trace_id": f"{span.context.trace_id:032x}",
                "span_id": f"{span.context.span_id:016x}",
                "parent_id": parent_id,
                "name": span.name,
                "start_time": span.start_time, # nanoseconds
                "end_time": span.end_time if event_type == "end" else None,     # nanoseconds
                "attributes": attrs,
                "status": span.status.status_code.name if event_type == "end" else "UNSET"
            }
        }

def setup_telemetry(app):
    """
    Configures OpenTelemetry for the FastAPI app.
    """
    resource = Resource(attributes={
        "service.name": "db-agent-backend"
    })
    
    provider = TracerProvider(resource=resource)
    
    # Use our custom processor
    processor = StreamSpanProcessor()
    provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app, excluded_urls="health")

def register_session_queue(session_id: str, queue: asyncio.Queue):
    """Registers a queue to receive spans for a given session."""
    # Ensure we get the running loop of the caller (main thread)
    loop = asyncio.get_running_loop()
    _session_queues[session_id] = (loop, queue)

def unregister_session_queue(session_id: str):
    """Unregisters a session."""
    if session_id in _session_queues:
        del _session_queues[session_id]

def get_tracer(name: str):
    return trace.get_tracer(name)

def instrument_adk_agents():
    """
    Monkey-patches BaseAgent.run_async to automatically wrap agent execution in OTel spans.
    This ensures all agents (LlmAgent, SequentialAgent, etc.) emit spans without manual decoration.
    """
    try:
        from google.adk.agents.base_agent import BaseAgent
        from opentelemetry.trace import Status, StatusCode
        
        logger.info("Instrumenting ADK Agents for OpenTelemetry...")

        if getattr(BaseAgent, "_is_instrumented", False):
            logger.info("ADK Agents already instrumented.")
            return

        # Original method
        original_run_async = BaseAgent.run_async

        # Wrapper
        async def instrumented_run_async(self, *args, **kwargs):
            tracer = trace.get_tracer("adk.agent")
            agent_name = getattr(self, "name", "UnknownAgent")
            agent_type = self.__class__.__name__
            
            # Attributes for the span
            attributes = {
                "agent.type": agent_type,
                "agent.name": agent_name
            }

            # Start span
            with tracer.start_as_current_span(f"Agent: {agent_name}", attributes=attributes) as span:
                try:
                    # Iterate the original async generator
                    async for event in original_run_async(self, *args, **kwargs):
                        yield event
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR))
                    raise

        # Apply patch
        BaseAgent.run_async = instrumented_run_async
        BaseAgent._is_instrumented = True
        logger.info("ADK Agents successfully instrumented.")

    except ImportError:
        logger.warning("Could not import google.adk.agents.base_agent. ADK instrumentation skipped.")
    except Exception as e:
        logger.error(f"Failed to instrument ADK Agents: {e}")
