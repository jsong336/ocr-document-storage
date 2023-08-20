import logging
from .api.documents import router as DocumentsRouter
from .api.auth import router as AuthRouter
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="2lkjdfslkdf")

    app.include_router(DocumentsRouter, prefix="/api/documents", tags=["documents"])
    app.include_router(AuthRouter, tags=["authentication"])
    return app
