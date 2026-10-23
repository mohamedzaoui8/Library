import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.routers.auth import auth
from app.api.v1.routers.google_auth import router as google_auth_router
from app.core.config import settings

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site="lax",
    https_only=os.getenv("ENVIRONMENT") == "production",
)
app.include_router(google_auth_router)
app.include_router(auth.router)
