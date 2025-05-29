from uuid import UUID

from pydantic import Field, BaseModel


class BaseUser(BaseModel):
    fullname: str | None = None


class ShowUser(BaseUser):
    id: UUID
    username: str
    email: str
    google_id: int
    is_active: bool
    is_superuser: bool
    is_banned: bool


class CreateUser(BaseUser):
    username: str = Field(min_length=4, max_length=8)
    google_id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class UpdateUser(BaseUser):
    username: str | None = Field(min_length=4, max_length=8, default=None)
