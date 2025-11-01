"""A2A Protocol data models using Pydantic."""
from typing import Any, List, Optional, Dict
from pydantic import BaseModel


class MessagePart(BaseModel):
    """A single part of a message (text, image, data, etc)."""
    kind: str  # "text", "image", "data", etc.
    text: Optional[str] = None
    data: Optional[Any] = None


class Message(BaseModel):
    """A2A Message format."""
    kind: str = "message"
    role: str  # "user" or "assistant"
    parts: List[MessagePart]
    messageId: Optional[str] = None


class PushNotificationConfig(BaseModel):
    """Webhook callback configuration from Telex."""
    url: str
    token: Optional[str] = None
    authentication: Optional[Dict[str, Any]] = None


class Configuration(BaseModel):
    """Request configuration."""
    acceptedOutputModes: Optional[List[str]] = None
    historyLength: Optional[int] = None
    pushNotificationConfig: Optional[PushNotificationConfig] = None
    blocking: bool = True


class Params(BaseModel):
    """Request parameters."""
    message: Message
    configuration: Optional[Configuration] = None


class A2ARequest(BaseModel):
    """Standard A2A JSON-RPC 2.0 request."""
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: Params


class A2AResponsePart(BaseModel):
    """A single part in A2A response."""
    kind: str
    text: str


class A2AResponseMessage(BaseModel):
    """Message in A2A response."""
    kind: str = "message"
    role: str = "assistant"
    parts: List[A2AResponsePart]


class A2AResponseResult(BaseModel):
    """Result structure for A2A response."""
    message: A2AResponseMessage


class A2AResponse(BaseModel):
    """Standard A2A JSON-RPC 2.0 response."""
    jsonrpc: str = "2.0"
    id: str
    result: A2AResponseResult


class A2AError(BaseModel):
    """A2A JSON-RPC 2.0 error response."""
    jsonrpc: str = "2.0"
    id: str
    error: Dict[str, Any]
