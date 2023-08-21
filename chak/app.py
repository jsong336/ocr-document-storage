import logging
import pathlib
from .api.documents import router as DocumentsRouter
from .api.auth import router as AuthRouter, get_user
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .db.schema import UserAccount
from .settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

root_dir = pathlib.Path(__file__).parent

templates = Jinja2Templates(directory=root_dir / "templates")


def create_app() -> FastAPI:
    app = FastAPI()
    app.mount("/static", StaticFiles(directory=root_dir / "static"), name="static")
    app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)

    @app.get("/")
    def index(request: Request, user: UserAccount = Depends(get_user)):
        return templates.TemplateResponse(
            "index.html", {"request": request, "user": user.model_dump()}
        )

    # @app.exception_handler(LoginRequiredException)
    # def handle_unauthenticate_error(request: Request, exec: HTTPException):
    #     return RedirectResponse("/login")

    app.include_router(DocumentsRouter, prefix="/api/documents", tags=["documents"])
    app.include_router(AuthRouter, tags=["authentication"])
    return app
