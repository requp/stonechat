import pytest
from jose import jwt

from app.auth.router import create_token
from app.core.config import settings


class TestCreateToken:

    @pytest.mark.asyncio
    async def test_create_token_positive(
            self, user_1
    ):
        token_data = await create_token(token_user_data=user_1)

        assert type(token_data) == dict

        assert set(token_data.keys()) == {"access_token"}

        token = token_data["access_token"]
        assert type(token) == str

        payload = jwt.decode(
            token=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert set(payload.keys()) == {"user_id", "exp", "sub"}

        assert payload["user_id"] == user_1.user_id
        assert payload["sub"] == user_1.username
