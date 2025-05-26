import logging
from http.client import HTTPException

from fastapi import APIRouter, WebSocket, WebSocketException, WebSocketDisconnect, status
from websockets.exceptions import ConnectionClosed

from app.auth.router import get_current_user
from app.auth.schemas import TokenUserData
from app.chat.schemas import ChatEventType, ChatEvent

# Логгер для модуля
logger = logging.getLogger(__name__)

v1_chat_router = APIRouter(prefix="/chat", tags=["chats"])


@v1_chat_router.websocket("/echo/ws")
async def websocket_echo(websocket: WebSocket):
    """
        Handles a WebSocket connection for echoing received messages back to the client.

        Args:
            websocket (WebSocket): The WebSocket connection object.

        The function accepts the connection, sends a welcome message, and echoes back any valid JSON messages received.
        It handles invalid message formats, disconnections, and unexpected errors, closing the connection appropriately.
    """

    await websocket.accept()
    logger.info("Новое WebSocket-соединение установлено")
    await websocket.send_json({"message": "Добро пожаловать"})
    try:
        while True:
            try:
                data = await websocket.receive_json()
                await websocket.send_json({"message": f"Вы написали: {data["message"]}"})
            except ValueError:
                await websocket.send_json({"message": f"Вы используете неверный формат сообщения"})
            except (WebSocketDisconnect, ConnectionClosed):
                logger.info('Disconnected')
                break
            except WebSocketException as e:
                await websocket.close(code=e.code, reason=e.reason)
                break
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}", exc_info=True)
        await websocket.close(code=1000, reason="Internal server error")


async def _get_current_user_or_exception(websocket: WebSocket, token: str) -> TokenUserData | None:
    """
        Authenticates a user from a provided token for a WebSocket connection.

        Args:
            websocket (WebSocket): The WebSocket connection object.
            token (str): The JWT token used to authenticate the user.

        Returns:
            TokenUserData | None: The authenticated user's data or None if authentication fails.

        Closes the WebSocket connection with a policy violation code if authentication fails.
    """
    try:
        return await get_current_user(token=token)
    except HTTPException:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION
        )
        return None


async def _send_everybody_in_chat(
        active_connections: set[WebSocket], chat_event: ChatEvent
):
    for connection in active_connections:
        await connection.send_json(
            chat_event.model_dump()
        )

active_connections: set[WebSocket] = set()
@v1_chat_router.websocket("/simple_group_chat/ws")
async def websocket_simple_group_chat(websocket: WebSocket, token: str) -> None:
    """
        Handles a WebSocket connection for a simple group chat.

        Args:
            websocket (WebSocket): The WebSocket connection object.
            token (str): The JWT token used to authenticate the user.
    """

    user: TokenUserData = await _get_current_user_or_exception(websocket, token)

    await websocket.accept()
    logger.info("Новое WebSocket-соединение установлено")
    active_connections.add(websocket)
    logger.info(f"{user.username} входит в чат")
    try:
        await _send_everybody_in_chat(
            active_connections=active_connections,
            chat_event=ChatEvent(
                type=ChatEventType.join,
                content=f"Добро пожаловать, {user.username}!"
            )
        )
        while True:
            data = await websocket.receive_json()
            await _send_everybody_in_chat(
                active_connections=active_connections,
                chat_event=ChatEvent(
                        type=ChatEventType.message,
                        content=data["message"],
                        sender=user.model_dump()
                    )
            )

    except ValueError:
        await websocket.send_json(
            ChatEvent(
                type=ChatEventType.error,
                content=f"Вы используете неверный формат сообщения",
            ).model_dump()
        )
    except (WebSocketDisconnect, ConnectionClosed):
        active_connections.remove(websocket)
        await _send_everybody_in_chat(
            active_connections=active_connections,
            chat_event=ChatEvent(
                type=ChatEventType.leave,
                content=f"Пользователь {user.username} вышел из чата"
            )
        )
        logger.info(f"{user.username} has disconnected!")

    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}", exc_info=True)
        logger.info(f"{user.username} has disconnected!")
