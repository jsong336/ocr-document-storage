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
    last_name: str
    first_name: str
    sub: t.Optional[str] = None
    picture_link: t.Optional[str] = None
    locale: t.Optional[str] = None


class FileMeta(_BaseModel):
    filename: str
    content_type: str
    file_size: int


class Document(BaseRootModel):
    owner_id: t.Optional[str] = Field(default=None)
    title: t.Optional[str] = Field(default=None)
    text_search: t.Optional[str] = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    link: t.Optional[str] = Field(default=None)
    file: t.Optional[FileMeta] = Field(default=None)
