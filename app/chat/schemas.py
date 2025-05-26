from enum import Enum

from pydantic import BaseModel

from app.auth.schemas import TokenUserData


class ChatEventType(str, Enum):
    message = "message"
    join = "join"
    leave = "leave"
    error = "error"


class ChatEvent(BaseModel):
    type: ChatEventType
    content: str
    sender: TokenUserData | None = None