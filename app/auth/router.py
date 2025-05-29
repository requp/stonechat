import logging
from datetime import datetime

from asyncpg.pgproto.pgproto import timedelta
from authlib.integrations.base_client import OAuthError
from fastapi import (
    HTTPException,
    status,
    APIRouter
)
from fastapi.params import Depends
from jose import jwt, JWTError

from app.auth.schemas import TokenUserData
from app.core.config import settings, oauth

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



@v1_auth_router.get(path="/google/callback")
async def auth_google(
        request: Request
):
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get("userinfo")
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        if user.get("iss") not in ["https://accounts.google.com", "accounts.google.com"]:
            logger.error(f"wrong iss {user.get("iss")}")
            raise HTTPException(
                status_code=401,
                detail="Google authentication failed."
            )


    except OAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    except Exception as e:
        logger.error(f"Google authentication failed: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail="Google authentication failed."
        )