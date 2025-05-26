import pytest
from fastapi import HTTPException, status

from app.auth.router import get_current_user


class TestGetCurrentUser:

    @pytest.mark.asyncio
    async def test_get_current_user_positive(
            self, user_1_token, user_1
    ):
        user_1_from_token = await get_current_user(token=user_1_token)
        assert user_1_from_token == user_1


    @pytest.mark.asyncio
    async def test_get_current_user_with_expired_token(
            self, user_1_expired_token
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=user_1_expired_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Невалидный токен"


    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(
            self, fake_token
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=fake_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Невалидный токен"
