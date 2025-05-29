from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import GoogleUserData
from app.user.generator import _generate_username
from app.user.model import User
from app.user.schema import ShowUser, CreateUser


def _user_data_from_google_user_data(
        google_user_data: GoogleUserData, username: str
) -> CreateUser:
    new_user_data = CreateUser(
        google_id=google_user_data.id,
        username=username,
        email=google_user_data.email,
        fullname=google_user_data.name
    )
    return new_user_data


async def _get_user_or_none(
        db: AsyncSession, email: str, google_id: str
) -> User | None:
    user: User | None = await db.scalar(
        select(User)
        .filter(
            or_(
                User.email == email,
                User.google_id == google_id
            )
        )
    )
    return user


async def _does_google_user_already_exist(
        db: AsyncSession, email: str, google_id: str
) -> bool:
    user: User | None = await _get_user_or_none(
        db=db,email=email, google_id=google_id
    )
    return bool(user)


class UserManager:

    @staticmethod
    async def get_user_or_raise_exception(
            db: AsyncSession, user_id: UUID
    ) -> User:
        user: User | None = await db.scalar(
            select(User).filter_by(id=user_id)
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with given id doesn't exist"
            )
        return user


    @staticmethod
    async def show_user(
            db: AsyncSession, user_id: UUID
    ) -> dict:
        user: User = await UserManager.get_user_or_raise_exception(
            db=db, user_id=user_id
        )
        return ShowUser(**user.__dict__).model_dump()


    @staticmethod
    async def create_user(
            db: AsyncSession, google_user_data: GoogleUserData
    ) -> User:
        does_user_exist = await _does_google_user_already_exist(
            db=db, email=google_user_data.email, google_id=google_user_data.id
        )
        if does_user_exist:
            raise HTTPException(
                detail="A user with given data already exists",
                status_code=status.HTTP_406_NOT_ACCEPTABLE
            )
        username: str = await _generate_username(db=db)
        user_data: CreateUser = _user_data_from_google_user_data(
            google_user_data=google_user_data, username=username
        )
        new_user: User = User(**user_data.model_dump())
        db.add(new_user)
        await db.commit()
        return new_user