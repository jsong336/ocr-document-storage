import logging
from .api.documents import router as DocumentsRouter
from .api.auth import router as AuthRouter
from .api.storage import router as StorageRouter
from .pages import include_render_pages
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from .settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)

    # @app.exception_handler(LoginRequiredException)
    # def handle_unauthenticate_error(request: Request, exec: HTTPException):
    #     return RedirectResponse("/login")

    app.include_router(DocumentsRouter, prefix="/api/documents", tags=["documents"])
    app.include_router(StorageRouter, prefix="/storage", tags=["storage"])
    app.include_router(AuthRouter, tags=["authentication"])
    include_render_pages(app)
    return app
