from uuid import UUID

from pydantic import BaseModel

class SimpleUserData(BaseModel):
    username: str
    fullname: str | None = None

class TokenUserData(BaseModel):
    username: str
    user_id: str