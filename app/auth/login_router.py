from app.core.config import oauth, settings
from fastapi import Request, APIRouter

from app.core.database import sync_engine

v1_login_router = APIRouter(prefix="/login", tags=["logins"])


@v1_login_router.get("/google")
async def login_google(request: Request):
    redirect_uri = f"{settings.PROD_URL}/api/v1/auth/google/callback"
    #print(oauth.google.client_kwargs)
    return await oauth.google.authorize_redirect(request, redirect_uri)
    # try:
    #     return await oauth.google.authorize_redirect(request, redirect_uri)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to initiate Google OAuth: {str(e)}")