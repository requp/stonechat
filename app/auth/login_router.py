from app.core.config import oauth, settings
from fastapi import Request, APIRouter

v1_login_router = APIRouter(prefix="/login", tags=["logins"])


@v1_login_router.get("/google")
async def login_google(request: Request):
    redirect_uri = f"{settings.PROD_URL}/api/v1/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)