import logging
from typing import Annotated

from asyncpg.pgproto.pgproto import timedelta
from authlib.integrations.base_client import OAuthError
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials
from httpx import AsyncClient
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.auth.router import logger, create_token, bearer_scheme
from app.auth.schemas import GoogleUserData, TokenUserData
from app.core.config import oauth, settings
from app.exceptions.common_exceptions import SomethingGotWrongHTTPException
from app.user.service import UserManager

logger = logging.getLogger(__name__)

async def _decode_jwt_token(token: str):
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


def _get_token_from_credentials(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]
) -> str:
    return credentials.credentials

async def _get_google_user_data_from_google_token(
        access_token: str, client: AsyncClient
) -> GoogleUserData | None:
    try:
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return GoogleUserData(**user_info_response.json())
    except Exception as e:
        logger.error(f"Error: {e}")
        raise SomethingGotWrongHTTPException


def _handle_auth_errors(exception: Exception) -> None:
    """
    Centralized error handling for authentication-related exceptions.

    Args:
        exception (Exception): The exception to handle.

    Raises:
        HTTPException: With appropriate status code and detail based on the exception type.
    """
    if isinstance(exception, OAuthError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    logger.error(f"Google authentication failed: {type(exception).__name__}: {exception}", exc_info=True)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Google authentication failed."
    )


async def _validate_google_token(request: Request) -> dict:
    """
    Validates the Google OAuth token and returns user info.

    Args:
        request (Request): The incoming request containing the OAuth token.

    Returns:
        dict: User info from the token.

    Raises:
        HTTPException: If user info is missing or issuer is invalid.
    """
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    if user_info.get("iss") not in ["https://accounts.google.com", "accounts.google.com"]:
        logger.error(f"wrong iss {user_info.get('iss')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed."
        )
    return token


async def _process_google_auth_or_raise_exception(
    request: Request, client: AsyncClient, db: AsyncSession
) -> RedirectResponse | None:
    """
    Processes Google authentication and redirects with a JWT token.

    Args:
        request (Request): The incoming request.
        client (AsyncClient): HTTP client for external requests.
        db (AsyncSession): Database session.

    Returns:
        RedirectResponse: Redirects to the frontend with a JWT token.

    Raises:
        HTTPException: If authentication fails, handled by handle_auth_errors.
    """
    try:
        token = await _validate_google_token(request)
        google_user_data = await _get_google_user_data_from_google_token(
            access_token=token["access_token"], client=client
        )
        user = await UserManager.get_or_create_user(
            db=db, google_user_data=google_user_data
        )
        token_user_data = TokenUserData(
            user_id=str(user.id), username=user.username
        )
        jwt_token = await create_token(token_user_data=token_user_data)
        return RedirectResponse(
            url=f"{settings.FRONTEND_SIMPLE_GROUP_URL}?token={jwt_token['access_token']}"
        )
    except Exception as e:
        _handle_auth_errors(e)


