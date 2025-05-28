import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_API: str = "/api/v1"

class Settings(BaseSettings):
    """
        Configuration settings for the application, loaded from environment variables or a .env file.

        Attributes:
            MODE (str): The application mode (e.g., development, production).
            SQL_PATH (str): The path to the SQL database file.
            ASYNC_ENGINE (str): The database engine string for asynchronous connections.
            SYNC_ENGINE (str): The database engine string for synchronous connections.
            SECRET_KEY (str): The secret key used for JWT encoding and decoding.
            ALGORITHM (str): The algorithm used for JWT encoding and decoding.
            UVICORN_PORT (int): The port number on which the Uvicorn server runs.
            UVICORN_HOST (str): The host address for the Uvicorn server.
    """

    MODE: str
    SQL_PATH: str
    ASYNC_ENGINE: str
    SYNC_ENGINE: str
    SECRET_KEY: str
    ALGORITHM: str
    UVICORN_PORT: int
    UVICORN_HOST: str

    @property
    def DATABASE_URL_async(self) -> str:
        return f"{self.ASYNC_ENGINE}:{self.SQL_PATH}"

    @property
    def DATABASE_URL_sync(self) -> str:
        return f"{self.SYNC_ENGINE}:{self.SQL_PATH}"


    model_config = SettingsConfigDict(
        env_file=f"{pathlib.Path(__file__).resolve().parent.parent.parent}/.env",
        extra="allow"
    )

settings = Settings()