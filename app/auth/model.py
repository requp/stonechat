import enum
from sqlalchemy import String, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.mixins.model_mixins.id_mixins import IDMixin
from app.mixins.model_mixins.timestamps_mixins import TimestampsMixin

from app.core.base import Base


class UserRoles(str, enum.Enum):
    admin = 'admin'
    user = 'user'

class User(IDMixin, TimestampsMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True
    )
    google_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True, index=True
    )
    fullname: Mapped[str | None] = mapped_column(String(200), default=None)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool]  = mapped_column(Boolean, default=False)
    role: Mapped[UserRoles] = mapped_column(default=UserRoles.user)