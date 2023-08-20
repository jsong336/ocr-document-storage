from .schema import BaseRootModel, UserAccount, Document
from .connection import collections
import datetime as dt
import pymongo
import typing as t
from typing_extensions import Unpack
from bson.objectid import ObjectId
from functools import wraps


class Kwargs(t.TypedDict, total=False):
    ...


TransactionOperation = t.Callable[[BaseRootModel, Unpack[Kwargs]], None]


def transaction(
    mode: t.Literal["create", "update"] = None
) -> t.Callable[[TransactionOperation], TransactionOperation]:
    def _transaction(fn: TransactionOperation) -> TransactionOperation:
        if fn.__name__.startswith("create"):
            mode = "create"
        elif fn.__name__.startswith("update"):
            mode = "update"
        if mode is None:
            raise ValueError(
                f"failed to automatically assign mode to function {fn.__name__}"
            )

        @wraps(fn)
        def wrapper(m: BaseRootModel, **kwargs: Unpack[Kwargs]):
            if mode == "create":
                if m.id is not None:
                    raise ValueError(f"{m.__repr_name__} already has id: {m.id}")
                m.created_at = dt.datetime.utcnow()
            m.updated_at = dt.datetime.utcnow()

            return fn(m, **kwargs)

        return wrapper

    return _transaction


def bson_object_id_to_str(body: dict[str, t.Any]):
    return {k: str(v) if isinstance(v, ObjectId) else v for k, v in body.items()}


def str_to_bson_object_id(body: dict[str, t.Any], keys: set = None):
    keys = {"_id"} | (keys if keys else set())
    return {k: ObjectId(v) if k in keys else v for k, v in body.items()}


@transaction()
def create_user_account(user: UserAccount):
    try:
        result = collections.UserAccount.insert_one(
            str_to_bson_object_id(user.model_dump(by_alias=True))
        )
    except pymongo.errors.DuplicateKeyError:
        raise ValueError(f"{user.email} already exists.")
    user.id = str(result.inserted_id)
    return


def get_user_account(email: str) -> UserAccount:
    results = collections.UserAccount.find_one(filter={"email": email})
    if results is None:
        raise ValueError(f"UserAccount with {email} not found")
    return UserAccount(**bson_object_id_to_str(results))


@transaction()
def create_document(doc: Document) -> Document:
    result = collections.Documents.insert_one(
        str_to_bson_object_id(doc.model_dump(by_alias=True), keys={"owner_id"})
    )
    doc.id = result.inserted_id
    return


def get_document(id: str) -> Document:
    results = collections.Documents.find_one(filter={"_id": ObjectId(id)})
    if results is None:
        raise ValueError(f"Document with {id} not found")
    return Document(**bson_object_id_to_str(results))
