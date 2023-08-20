from .schema import BaseRootModel, UserAccount, Document
from .connection import collections
import datetime as dt
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


@transaction()
def create_user_account(user: UserAccount):
    result = collections.UserAccount.insert_one(user.model_dump())
    user.id = str(result.inserted_id)
    return


def get_user_account(id: str) -> UserAccount:
    results = collections.UserAccount.find_one(filter={"_id": ObjectId(id)})

    results["_id"] = str(results["_id"])
    return UserAccount(**results)


@transaction()
def create_document(doc: Document) -> Document:
    result = collections.Documents.insert_one(doc.model_dump())
    doc.id = result.inserted_id
    return


def get_document(id: str) -> Document:
    results = collections.Documents.find_one(filter={"_id": ObjectId(id)})
    results["_id"] = str(results["_id"])
    return Document(**results)