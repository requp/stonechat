import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict
from authlib.integrations.starlette_client import OAuth

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
            GOOGLE_CLIENT_ID (str): The client ID for Google OAuth authentication.
            GOOGLE_CLIENT_SECRET (str): The client secret for Google OAuth authentication.
            PROD_HOST (str): The host address for the production server.
            PROD_PORT (int): The port number for the production server
    """

    MODE: str
    SQL_PATH: str
    ASYNC_ENGINE: str
    SYNC_ENGINE: str
    SECRET_KEY: str
    ALGORITHM: str
    UVICORN_PORT: int
    UVICORN_HOST: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    PROD_HOST: str
    PROD_PORT: int

    @property
    def DATABASE_URL_async(self) -> str:
        return f"{self.ASYNC_ENGINE}:{self.SQL_PATH}"

    @property
    def DATABASE_URL_sync(self) -> str:
        return f"{self.SYNC_ENGINE}:{self.SQL_PATH}"

    @property
    def PROD_URL(self) -> str:
        return f"http://{self.PROD_HOST}:{self.PROD_PORT}"


    model_config = SettingsConfigDict(
        env_file=f"{pathlib.Path(__file__).resolve().parent.parent.parent}/.env",
        extra="allow"
    )

settings = Settings()


oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    authorize_state=settings.SECRET_KEY,
    redirect_uri=f"{settings.PROD_URL}/api/v1/auth",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid email profile"},
)