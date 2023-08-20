import logging
from .api.documents import router as DocumentsRouter
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI()
    
    app.include_router(DocumentsRouter, prefix="/api/documents", tags=["documents"])

    return app
