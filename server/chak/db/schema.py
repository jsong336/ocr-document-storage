from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, ConfigDict
import datetime as dt
import typing as t
    

class UserAccount(BaseModel):
    id: t.Optional[str] = Field(default=None, alias="_id")
    email: EmailStr = Field()

    created_at: t.Optional[dt.datetime] = Field(default=None)
    updated_at: t.Optional[dt.datetime] = Field(default=None)

    model_config = ConfigDict(populate_by_name=True)