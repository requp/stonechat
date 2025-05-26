from typing import AsyncGenerator

import pytest_asyncio

from fastapi import WebSocket
from fastapi.testclient import TestClient
from starlette.testclient import WebSocketTestSession

from app.main import app
from tests.conftest import WEBSOCKET_URL

ECHO_CHAT_API_URL: str = f"{WEBSOCKET_URL}/api/v1/chat/echo/ws"
SIMPLE_GROUP_CHAT_API_URL: str = f"{WEBSOCKET_URL}/api/v1/chat/simple_group_chat/ws"


@pytest_asyncio.fixture
async def echo_websocket() -> AsyncGenerator[WebSocketTestSession]:
    client = TestClient(app)
    with client.websocket_connect(ECHO_CHAT_API_URL) as websocket:
        yield websocket


@pytest_asyncio.fixture
async def echo_websocket_skipped_welcome(echo_websocket) -> AsyncGenerator[WebSocketTestSession]:
    echo_websocket.receive_json()
    yield echo_websocket


async def simple_group_chat_websocket() -> AsyncGenerator[WebSocketTestSession]:
    client = TestClient(app)
    with client.websocket_connect(SIMPLE_GROUP_CHAT_API_URL) as websocket:
        yield websocket


# @pytest_asyncio.fixture()
# async def simple_group_chat_websocket_group():
#     websockets_group = set()
#     for _ in range(3):
#         websocket = simple_group_chat_websocket()
#         websockets_group.add(websocket)
#     yield websockets_group


@pytest_asyncio.fixture()
async def simple_group_chat_websocket_group(user_1_token, user_2_token):
    url_1 = SIMPLE_GROUP_CHAT_API_URL+f"?token={user_1_token}"
    url_2 = SIMPLE_GROUP_CHAT_API_URL + f"?token={user_2_token}"
    client = TestClient(app)
    with (
        client.websocket_connect(url_1) as ws1,
        client.websocket_connect(url_2) as ws2,
    ):
        yield ws1, ws2