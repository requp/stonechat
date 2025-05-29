from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from random import choice

from app.user.model import User


async def _is_username_taken(db: AsyncSession, username: str) -> bool:
    return bool(
        await db.scalar(select(User).filter_by(username=username))
    )

async def _generate_username(db: AsyncSession) -> str:
    is_username_taken: bool = True
    new_username: str = ""
    while is_username_taken:
        new_username = "user "
        for _ in range(9):
            new_username += choice("0123456789")
        is_username_taken = await _is_username_taken(db=db, username=new_username)
    return new_username