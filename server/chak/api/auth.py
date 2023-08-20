from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import json
import typing as t
from ..settings import settings
from ..db.repository import create_user_account, get_user_account
from ..db.schema import UserAccount

# https://colab.research.google.com/github/kmcentush/site/blob/master/_notebooks/2020-08-16-fastapi_google_oauth_part1.ipynb#scrollTo=LBUPzo_inL4M
# https://docs.authlib.org/en/latest/client/frameworks.html#frameworks-clients
router = APIRouter()

oauth = OAuth()

config_url = "https://accounts.google.com/.well-known/openid-configuration"

with open(settings.google_cloud_config.oauth_client_credential, "r") as f:
    google_client_credential = json.load(f).get("web")

oauth.register(
    name="google",
    server_metadata_url=config_url,
    client_kwargs={"scope": "openid email profile"},
    client_id=google_client_credential.get("client_id"),
    client_secret=google_client_credential.get("client_secret"),
)


@router.get("/register", tags=["authentication"])
async def redirect_oauth_register(request: Request):
    if "user" in request.session:
        request.session.pop("user", None)
        # return RedirectResponse(url='/logout')

    redirect_url = request.url_for("register")
    return await oauth.google.authorize_redirect(request, redirect_url)


@router.get("/login", tags=["authentication"])
async def redirect_oauth_login(request: Request):
    if "user" in request.session:
        request.session.pop("user", None)
        # return RedirectResponse(url='/logout')

    redirect_url = request.url_for("login")
    return await oauth.google.authorize_redirect(request, redirect_url)


@router.get("/auth/login")
async def login(request: Request):
    token = await oauth.google.authorize_access_token(request)
    token = dict(token)
    userinfo = token.get("userinfo")
    account = google_user_info_to_user_account(userinfo)

    try:
        account = get_user_account(account.email)
    except ValueError:
        raise HTTPException(401)

    return RedirectResponse(url="/")


def google_user_info_to_user_account(userinfo: dict[str, t.Any]) -> UserAccount:
    account = UserAccount(
        email=userinfo.get("email"),
        last_name=userinfo.get("family_name"),
        first_name=userinfo.get("given_name"),
        sub=userinfo.get("sub"),
        picture_link=userinfo.get("picture"),
        locale=userinfo.get("locale"),
    )
    return account


@router.get("/auth/register")
async def register(request: Request):
    token = await oauth.google.authorize_access_token(request)
    token = dict(token)

    userinfo = token.get("userinfo")
    if not userinfo.get("email_verified"):
        raise HTTPException(401, "Account is not verified")

    account = google_user_info_to_user_account(userinfo)
    try:
        create_user_account(account)
    except ValueError as e:
        return HTTPException(status_code=400, detail=e.args[0])

    return RedirectResponse(url="/")
