from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request, FastAPI, Depends
from .db.repository import DocumentQuery
from .db.schema import UserAccount
from .api.auth import get_user_if_exists
import typing as t
import pathlib
import jinja2

root_dir = pathlib.Path(__file__).parent

templates = Jinja2Templates(directory=root_dir / "templates")


def render_index(request: Request, user:t.Optional[UserAccount] = Depends(get_user_if_exists)):
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": user}
    )


def render_pages(
        request: Request, 
        path:str, 
        query: t.Annotated[DocumentQuery, Depends(DocumentQuery)],
        user:t.Optional[UserAccount] = Depends(get_user_if_exists)
    ):
    try:
        context = {"request": request, "user": user}
        match path:
            case "home":
                context["documents"] = query()
        response = templates.TemplateResponse(
            f"{path}.html", context
        )
    except jinja2.exceptions.TemplateNotFound:
        response = templates.TemplateResponse(
            f"errors/404.html", { "request": request, "user": user }
        )
    return response


def include_render_pages(app: FastAPI):
    app.mount("/static", StaticFiles(directory=root_dir / "static"), name="static")
    app.get("/")(render_index)
    app.get("/pages/{path}")(render_pages)
    
    return 