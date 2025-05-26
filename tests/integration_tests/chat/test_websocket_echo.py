import logging
from time import sleep


class TestWebsocketEcho:
    """
        A test class for verifying the functionality of the WebSocket echo endpoint.

        This class contains test methods to validate the behavior of the WebSocket echo
        endpoint, including receiving a welcome message, handling disconnections, and
        processing JSON and text messages.
    """

    async def test_echo_welcome(
            self, echo_websocket
    ) -> None:
        """
           Tests that the WebSocket echo endpoint sends a correct welcome message upon connection.
        """

        response = echo_websocket.receive_json()
        assert type(response) is dict
        assert tuple(response.keys()) == ("message",)
        assert response["message"] == "Добро пожаловать"


    async def test_echo_disconnect_log(
            self, echo_websocket_skipped_welcome, caplog
    ) -> None:
        """
            Tests sending a JSON message to the WebSocket echo endpoint and receiving the echoed response.
        """
        with caplog.at_level(logging.INFO):
            echo_websocket_skipped_welcome.close()
            sleep(1)
            assert "Disconnected" in caplog.text


    async def test_echo_send_json(
            self, echo_websocket_skipped_welcome
    ) -> None:
        """
            Tests sending a JSON message to the WebSocket echo endpoint and receiving the echoed response.
        """

        echo_websocket_skipped_welcome.send_json({"message": "я люблю бананы"})
        response = echo_websocket_skipped_welcome.receive_json()
        assert response["message"] == "Вы написали: я люблю бананы"


    async def test_echo_send_text(
            self, echo_websocket_skipped_welcome
    ) -> None:
        """
            Tests sending text messages to the WebSocket echo endpoint, both valid JSON and invalid text.
        """
        echo_websocket_skipped_welcome.send_text('{"message":"я люблю бананы"}')
        response = echo_websocket_skipped_welcome.receive_json()
        assert response["message"] == "Вы написали: я люблю бананы"

        echo_websocket_skipped_welcome.send_text("я люблю яблоки")
        response = echo_websocket_skipped_welcome.receive_json()
        assert response["message"] == "Вы используете неверный формат сообщения"