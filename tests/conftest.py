URL: str = 'http://127.0.0.1:8888'
URL_API_V1: str = f'{URL}/api/v1'
WEBSOCKET_URL: str = "ws://127.0.0.1:8888"
WEBSOCKET_URL_API_V1: str = f'{WEBSOCKET_URL}/api/v1'


from datetime import timedelta
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.auth.router import create_token
from app.auth.schemas import TokenUserData
from app.main import app
from tests.conftest import URL_API_V1

AUTH_API_URL: str = URL_API_V1 + "/auth"
@pytest_asyncio.fixture
async def async_user_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=AUTH_API_URL) as client:
        yield client



@pytest.fixture
def user_1_data() -> dict:
    return {
        "user_id": str(uuid4()),
        "username": "user_1",
    }

@pytest.fixture
def user_1(user_1_data) -> TokenUserData:
    return TokenUserData(**user_1_data)

@pytest.fixture
def fake_token() -> str:
    return "fake_token"


@pytest_asyncio.fixture
async def user_1_token(user_1) -> str:
    return (
        await create_token(
            token_user_data=user_1, expires_delta=timedelta(days=365)
        )
    )["access_token"]


@pytest_asyncio.fixture
async def user_1_expired_token(user_1) -> str:
    return (
        await create_token(
            token_user_data=user_1, expires_delta=timedelta(days=-1)
        )
    )["access_token"]


@pytest.fixture
def user_2_data() -> dict:
    return {
        "user_id": str(uuid4()),
        "username": "user_2"
    }


@pytest.fixture
def user_2(user_2_data) -> TokenUserData:
    return TokenUserData(**user_2_data)


@pytest_asyncio.fixture
async def user_2_token(user_2) -> str:
    return (
        await create_token(
            token_user_data=user_2, expires_delta=timedelta(days=365)
        )
    )["access_token"]