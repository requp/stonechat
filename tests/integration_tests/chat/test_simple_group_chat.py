import asyncio
import logging
from time import sleep

from starlette.websockets import WebSocket

from app.auth.schemas import TokenUserData
from app.chat.schemas import ChatEvent, ChatEventType

# def _skip_n_ws_receives(websocket: WebSocket, n: int):
#     for _ in range(n):
#         print(websocket.receive_json())


class TestSimpleGroupChat:

    async def test_simple_group_chat_positive(
            self, simple_group_chat_websocket_group, user_2_data, user_1_data
    ) -> None :
        ws_1, ws_2 = simple_group_chat_websocket_group

        response_1 = ws_1.receive_json()
        assert type(response_1) == dict

        assert set(response_1.keys()) == {"content", "type", "sender"}

        assert response_1["type"] == "join"
        assert response_1["content"] == "Добро пожаловать, user_1!"

        response_2 =  ws_2.receive_json()
        assert response_2["content"] == "Добро пожаловать, user_2!"

        user_2_message = {"message": "я люблю бананы"}
        ws_2.send_json(user_2_message)

        ws_1.receive_json()
        response_1 = ws_1.receive_json()
        ws_2.receive_json()

        assert response_1["content"] == user_2_message["message"]

        assert response_1["sender"] == user_2_data

        user_1_message: dict = {"message": "а мне вообще ничего не нравится"}

        ws_1.send_json(user_1_message)

        response_2 = ws_2.receive_json()

        assert response_2["content"] == user_1_message["message"]
        assert response_2["sender"] == user_1_data


    async def test_echo_disconnect_log(
            self, simple_group_chat_websocket_group, caplog
    ) -> None:
        """
            Tests sending a JSON message to the WebSocket .
        """
        ws_1, ws_2 = simple_group_chat_websocket_group
        with caplog.at_level(logging.INFO):
            ws_1.close()
            sleep(0.5)
            assert "user_1 has disconnected!" in caplog.text

            ws_2.receive_json() # skip join message
            response_2 = ws_2.receive_json()
            assert response_2["type"] == "leave"

            assert response_2["content"] == "Пользователь user_1 вышел из чата"

            ws_2.close()
            sleep(0.5)
            assert "user_2 has disconnected!" in caplog.text