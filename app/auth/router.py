import logging
from datetime import datetime
from typing import Annotated

from asyncpg.pgproto.pgproto import timedelta
from fastapi import (
    status,
    APIRouter,
    Request
)
from fastapi.params import Depends
from fastapi.security import HTTPBearer
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import RedirectResponse

from app.auth.service import _process_google_auth_or_raise_exception, _decode_jwt_token, _get_token_from_credentials
from app.core.config import settings
from app.depends.async_client import make_request
from app.auth.schemas import TokenUserData
from app.mixins.db_mixin import get_db

# Логгер для модуля
logger = logging.getLogger(__name__)

v1_auth_router = APIRouter(prefix="/auth", tags=["auth"])


async def get_current_user_ws(token: str) -> TokenUserData | None:
    """
        Retrieves the current user's data from a JWT token.

        Args:
            token (str): The JWT token provided in the request header.

        Returns:
            TokenUserData | None: An object containing user data (username, user_id) or None if the token is invalid.

        Raises:
            HTTPException: If the token is invalid (401) or expired (403).
    """

    return await _decode_jwt_token(token)


bearer_scheme = HTTPBearer()


async def get_current_user(
        token: Annotated[str, Depends(_get_token_from_credentials)]
) -> TokenUserData | None:
    """
        Retrieves the current user's data from a JWT token.

        Args:
            token (str): The JWT token provided in the request header.

        Returns:
            TokenUserData | None: An object containing user data (username, user_id) or None if the token is invalid.

        Raises:
            HTTPException: If the token is invalid (401) or expired (403).
    """

    return await _decode_jwt_token(token)


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


@v1_auth_router.get(path="/google/callback")
async def auth_google(
    request: Request,
    client: Annotated[AsyncClient, Depends(make_request)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> RedirectResponse:
    """
    Handles Google OAuth callback, processes authentication, and redirects to frontend.

    Args:
        request (Request): The incoming request.
        client (AsyncClient): HTTP client for external requests.
        db (AsyncSession): Database session.

    Returns:
        RedirectResponse: Redirects to the frontend with a JWT token.
    """
    return await _process_google_auth_or_raise_exception(request, client, db)

