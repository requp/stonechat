import pytest
from fastapi import status

from app.auth.router import get_current_user
from app.auth.schemas import TokenUserData


class TestAuthToken:

    @pytest.mark.asyncio
    async def test_create_token_positive(
            self, user_1_data, async_user_client
    ):
        response = await async_user_client.post(url='/token', json=user_1_data)

        assert response.status_code == status.HTTP_201_CREATED
        json_data: dict = response.json()

        assert set(json_data.keys()) == {"access_token"}
        assert json_data["access_token"]

        user = await get_current_user(token=json_data["access_token"])
        assert isinstance(user, TokenUserData)
        assert user_1_data["username"] == user.username
        assert user_1_data["user_id"] == user.user_id

