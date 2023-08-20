from __future__ import annotations
from pydantic import BaseModel as _BaseModel, EmailStr, Field, ConfigDict
import datetime as dt
import typing as t

base_model_config = ConfigDict(populate_by_name=True)


class BaseRootModel(_BaseModel):
    id: t.Optional[str] = Field(default=None, alias="_id")

    created_at: t.Optional[dt.datetime] = Field(default=None)
    updated_at: t.Optional[dt.datetime] = Field(default=None)

    model_config = base_model_config


class UserAccount(BaseRootModel):
    email: EmailStr = Field()


class Document(BaseRootModel):
    owner_id: str
    title: str = Field(default="")
    doc: t.Optional[str] = Field(default=None)
    tags: list[str] = Field(default_factory=list)
