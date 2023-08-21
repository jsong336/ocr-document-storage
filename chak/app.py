import logging
from .api.documents import router as DocumentsRouter
from .api.auth import router as AuthRouter, get_user, LoginRequiredException
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from .db.schema import UserAccount
from .settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)

    @app.get("/")
    def index(request: Request, user: UserAccount = Depends(get_user)):
        return HTMLResponse(
            f"""
            <h1> Welcome! {user.first_name}!</h1>
        """
        )

    # @app.exception_handler(LoginRequiredException)
    # def handle_unauthenticate_error(request: Request, exec: HTTPException):
    #     return RedirectResponse("/login")

    app.include_router(DocumentsRouter, prefix="/api/documents", tags=["documents"])
    app.include_router(AuthRouter, tags=["authentication"])
    return app
