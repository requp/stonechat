import logging
from uuid import UUID

from fastapi import APIRouter, status, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.auth.router import get_current_user_ws, get_current_user
from app.user.service import UserManager
from app.mixins.db_mixin import get_db

logger = logging.getLogger(__name__)

v1_user_router = APIRouter(prefix="/users", tags=["users"])


@v1_user_router.get(path="/{user_id}", response_model=dict)
async def show_user(
        get_user: Annotated[dict, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
        user_id: Annotated[UUID, Path()]
) -> dict:
    user_data: dict = await UserManager.show_user(
        user_id=user_id, db=db
    )
    return {
        "data": user_data,
        "status_code": status.HTTP_200_OK,
        "detail": "Successful"
    }