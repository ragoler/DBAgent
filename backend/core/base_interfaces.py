from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Any
from backend.core.generic_types import ChatMessage, StreamChunk

class BaseAgent(ABC):
    """Abstract base class for all specialized agents."""
    @property
    @abstractmethod
    def name(self) -> str:
        pass

class BaseRunner(ABC):
    """
    Abstract base class for running agent loops.
    Wraps platform-specific logic (ADK, LangChain, etc.)
    """
    @abstractmethod
    async def run_stream(
        self, 
        user_id: str, 
        session_id: str, 
        message: str
    ) -> AsyncGenerator[StreamChunk, None]:
        pass

    @abstractmethod
    async def get_session(self, user_id: str, session_id: str) -> Any:
        """Retrieve session data for a specific user/session."""
        pass
