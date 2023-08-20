from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, ConfigDict
import datetime as dt
import typing as t
    

base_model_config = ConfigDict(populate_by_name=True) 
class UserAccount(BaseModel):
    id: t.Optional[str] = Field(default=None, alias="_id")
    email: EmailStr = Field()

    created_at: t.Optional[dt.datetime] = Field(default=None)
    updated_at: t.Optional[dt.datetime] = Field(default=None)

    model_config = base_model_config


class PhotoDocument(BaseModel):
    id: t.Optional[str] = Field(default=None, alias="_id")
    
    title: str = Field(default="")
    doc: str = Field(default="")
    tags: list[str] = Field(default_factory=list)

    created_at: t.Optional[dt.datetime] = Field(default=None)
    updated_at: t.Optional[dt.datetime] = Field(default=None)
    
    model_config = base_model_config