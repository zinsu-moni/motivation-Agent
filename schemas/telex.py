from pydantic import BaseModel, Field
from typing import Any, Optional, Union, List
from datetime import datetime


class TelexRequest(BaseModel):
    telex: str = Field(default="2.0", description="Telex version")
    method: str = Field(description="Method to call")
    params: Optional[dict] = Field(default=None, description="Method parameters")
    id: Optional[Union[str, int]] = Field(default=None, description="Request ID")

class TelexResponse(BaseModel):
    telex: str = Field(default="2.0", description="Telex version")
    result: Optional[Any] = Field(default=None, description="Method result")
    error: Optional[dict] = Field(default=None, description="Error object")
    id: Optional[Union[str, int]] = Field(default=None, description="Request ID")

class TelexError(BaseModel):
    code: int = Field(description="Error code")
    message: str = Field(description="Error message")
    data: Optional[Any] = Field(default=None, description="Additional error data")

class MessagePart(BaseModel):
    content: str = Field(description="Message content")
    type: Optional[str] = Field(default="text", description="Content type")

class Message(BaseModel):
    kind: str = Field(default="message", description="Message kind")
    role: str = Field(description="Message role (user/assistant)")
    parts: List[MessagePart] = Field(description="Message parts")

class Agent(BaseModel):
    name: str = Field(description="Agent name")
    title: str = Field(description="Agent title")
    version: Optional[str] = Field(default="1.0.0", description="Agent version")

class SendMessageParams(BaseModel):
    message: Message = Field(description="Message to process")
    user_id: Optional[str] = Field(default=None, description="User ID for personalization")

class SendMessageResult(BaseModel):
    response: str = Field(description="Motivational response")
    agent: Agent = Field(description="Agent information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class OnboardUserParams(BaseModel):
    name: str = Field(description="User's name")
    email: str = Field(description="User's email address")

class OnboardUserResult(BaseModel):
    user_id: str = Field(description="Generated user ID")
    message: str = Field(description="Welcome message")
    agent: Agent = Field(description="Agent information")

class SetReminderParams(BaseModel):
    user_id: str = Field(description="User ID")
    reminder_text: str = Field(description="Reminder message")
    scheduled_time: str = Field(description="When to send reminder (e.g., '8 PM', 'tomorrow 9 AM')")

class SetReminderResult(BaseModel):
    reminder_id: str = Field(description="Generated reminder ID")
    message: str = Field(description="Confirmation message")
    scheduled_for: datetime = Field(description="Scheduled datetime")
    agent: Agent = Field(description="Agent information")

class SendMotivationEmailParams(BaseModel):
    user_id: str = Field(description="User ID")
    custom_message: Optional[str] = Field(default=None, description="Custom motivation request")

class SendMotivationEmailResult(BaseModel):
    message: str = Field(description="Confirmation message")
    sent_to: str = Field(description="Email address")
    agent: Agent = Field(description="Agent information")