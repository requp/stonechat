import logging
from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

from app.depends.async_client import make_request

logger = logging.getLogger(__name__)

async def _get_user_info_from_google_token(
        access_token: str, client: Annotated[AsyncClient, Depends(make_request)]
) -> dict | None:
    try:
        user_info_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return user_info_response.json()
    except Exception as e:
        logger.error(f"Error: {e}")

