import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

import app.models.registry as _model_registry
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.authors import router as authors_router
from app.api.v1.routers.books import router as books_router
from app.api.v1.routers.categories import router as categories_router
from app.api.v1.routers.google_auth import router as google_auth_router
from app.api.v1.routers.reading import router as reading_router
from app.core.config import settings

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    same_site="lax",
    https_only=os.getenv("ENVIRONMENT") == "production",
)
app.include_router(google_auth_router)
app.include_router(auth_router)
app.include_router(authors_router)
app.include_router(categories_router)
app.include_router(books_router)
app.include_router(reading_router)
