import logging
from datetime import datetime
from typing import Annotated

from asyncpg.pgproto.pgproto import timedelta
from fastapi import (
    HTTPException,
    status,
    APIRouter,
    Depends
)
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.auth.schemas import TokenUserData, GoogleUserData
from app.core.config import settings
from app.main import app
from app.mixins.db_mixin import get_db
from app.user.model import User
from app.user.schema import CreateUser
from app.user.service import UserManager, _user_data_from_google_user_data, _does_google_user_already_exist, \
    _get_user_or_none

# Логгер для модуля
logger = logging.getLogger(__name__)

v1_auth_router = APIRouter(prefix="/auth", tags=["auth"])

async def get_current_user(token: str) -> TokenUserData | None:
    """
        Retrieves the current user's data from a JWT token.

        Args:
            token (str): The JWT token provided in the request header.

        Returns:
            TokenUserData | None: An object containing user data (username, user_id) or None if the token is invalid.

        Raises:
            HTTPException: If the token is invalid (401) or expired (403).
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        expire: timedelta = payload.get("exp")

        if any([username, expire, user_id]) is None:
            raise credentials_exception
        return TokenUserData(
            username=username,
            user_id=user_id
        )
    except JWTError:
        raise credentials_exception


@v1_auth_router.post(
    path="/token", response_model=dict, status_code=status.HTTP_201_CREATED
)
async def create_token(
        token_user_data: TokenUserData,
        expires_delta: timedelta = timedelta(minutes=20)
) -> dict:
    """
        Creates a JWT token based on user data.

        Args:
            token_user_data (TokenUserData): User data containing username and user_id.
            expires_delta (timedelta, optional): Token expiration time. Defaults to 20 minutes.

        Returns:
            dict: A dictionary containing the "access_token" with the generated JWT token.
    """
    user_data: dict = {
        "sub": token_user_data.username,
        "user_id": token_user_data.user_id,
        "exp": datetime.now() + expires_delta
    }
    token: str = jwt.encode(
        key=settings.SECRET_KEY, algorithm=settings.ALGORITHM, claims=user_data
    )
    return {
        "access_token": token
    }


async def authenticate_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        google_user_data: GoogleUserData
):
    user: User | None = await _get_user_or_none(
        db=db, email=google_user_data.email, google_id=google_user_data.id
    )
    if not user:
        user = await UserManager.create_user(
            db=db, google_user_data=google_user_data
        )
    return user
