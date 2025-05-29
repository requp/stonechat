import logging

import uvicorn
from fastapi import FastAPI, APIRouter

from app.auth.router import v1_auth_router
from app.user.router import v1_user_router
from app.chat.router import v1_chat_router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(v1_chat_router)
api_v1_router.include_router(v1_auth_router)
api_v1_router.include_router(v1_user_router)

app.include_router(api_v1_router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.UVICORN_HOST, port=settings.UVICORN_PORT)