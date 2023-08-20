import logging
from . import db
from fastapi import FastAPI

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI()

    return app
