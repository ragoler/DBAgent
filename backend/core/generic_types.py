from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class StreamChunk(BaseModel):
    text: Optional[str] = None
    is_thinking: bool = False
    tool_name: Optional[str] = None
    is_complete: bool = False
