from typing import Any
from .schema import BaseRootModel, UserAccount, Document
from .connection import collections
import datetime as dt
import pymongo
import typing as t
from typing_extensions import Unpack
from bson.objectid import ObjectId
from functools import wraps
from dateutil.parser import parse as parse_dt, ParserError


class Kwargs(t.TypedDict, total=False):
    ...


DatetimeRange = tuple[dt.datetime, dt.datetime]

TransactionOperation = t.Callable[[BaseRootModel, Unpack[Kwargs]], None]


def transaction(
    mode: t.Literal["create", "update"] = None
) -> t.Callable[[TransactionOperation], TransactionOperation]:
    def _transaction(fn: TransactionOperation) -> TransactionOperation:
        nonlocal mode
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


def get_user_account_by_id(id: str) -> UserAccount:
    results = collections.UserAccount.find_one(filter={"_id": ObjectId(id)})
    if results is None:
        raise ValueError(f"UserAccount with {id} not found")
    return UserAccount(**bson_object_id_to_str(results))


def get_user_account_by_email(email: str) -> UserAccount:
    results = collections.UserAccount.find_one(filter={"email": email})
    if results is None:
        raise ValueError(f"UserAccount with {email} not found")
    return UserAccount(**bson_object_id_to_str(results))


@transaction()
def create_document(doc: Document) -> Document:
    result = collections.Documents.insert_one(
        str_to_bson_object_id(doc.model_dump(by_alias=True), keys={"owner_id"})
    )
    doc.id = str(result.inserted_id)
    return


def get_document_by_id(id: str) -> Document:
    results = collections.Documents.find_one(filter={"_id": ObjectId(id)})
    if results is None:
        raise ValueError(f"Document with {id} not found")
    return Document(**bson_object_id_to_str(results))


@transaction()
def update_document(doc: Document, updates: dict[str, t.Any]):
    collections.Documents.update_one(
        filter={"_id": ObjectId(doc.id)},
        update={
            "$set": {
                **updates,
                "updated_at": doc.updated_at,
            },
        },
    )
    return


def document_results_to_documents(results: list[dict[str, t.Any]]):
    documents = []
    for result in results:
        documents.append(Document(**bson_object_id_to_str(result)))
    return documents


def datetime_range_split(datetime_range: str) -> DatetimeRange:
    if datetime_range is None:
        return None
    start, end = datetime_range.split("~")
    try:
        return (
            parse_dt(start.strip()) if start else dt.datetime(2023, 1, 1),
            parse_dt(end.strip()) if end else dt.datetime.now(),
        )
    except ParserError:
        raise ValueError(f"Unable to parse {datetime_range}")


class DocumentQuery:
    def __init__(
        self,
        title: t.Optional[str] = None,
        q: t.Optional[str] = None,
        tags: t.Optional[str] = None,
        updated_at_range: t.Optional[str] = None,
        created_at_range: t.Optional[str] = None,
        n: int = 15,
        page: int = 0,
        sortby: str = "updated_at",
        ascending: bool = False,
    ) -> None:
        self.title = title
        self.q = q
        self.tags = tags
        self.updated_at_range = datetime_range_split(updated_at_range)
        self.created_at_range = datetime_range_split(created_at_range)
        self.n = n
        self.page = page
        self.sortby = sortby
        self.ascending = pymongo.ASCENDING if ascending else pymongo.DESCENDING

    def __call__(self, exclude: t.Optional[set] = None) -> Any:
        query = {}
        if self.title:
            query["title"] = f"/{self.title}/i"
        if self.q:
            query["$text"] = {
                "$search": self.q,
                "$caseSensitive": False,
                "$diacriticSensitive": False,
            }
        if self.tags:
            query["tags"] = self.tags
        if self.updated_at_range:
            updated_at_start, updated_at_end = self.updated_at_range
            query["updated_at"] = {
                "$gte": updated_at_start,
                "$lte": updated_at_end,
            }
        if self.created_at_range:
            created_at_start, created_at_end = self.created_at_range
            query["created_at"] = {
                "$gte": created_at_start,
                "$lte": created_at_end,
            }

        fields = {k: 0 for k in Document.__fields__ if k in (exclude or ())}
        results = collections.Documents.find(query, fields).sort(
            [(self.sortby, self.ascending)]
        )
        return document_results_to_documents(
            results.skip(self.page * self.n).limit(self.n)
        )


def query_documents(*args, **kwargs) -> list[Document]:
    query = DocumentQuery(*args, **kwargs)
    return query()
