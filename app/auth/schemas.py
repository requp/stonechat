from pydantic import BaseModel


class TokenUserData(BaseModel):
    username: str
    user_id: str


class GoogleUserData(BaseModel):
    id: str
    email: str
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    verified_email: bool = True
    picture: str | None = None