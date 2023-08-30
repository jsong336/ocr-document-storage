from __future__ import annotations
from pydantic import (
    BaseModel as _BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    model_validator,
)
from enum import Enum
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
    file_size: t.Optional[int] = None
    link: t.Optional[str] = None


class DocumentPermission(Enum):
    READ = "permission.document.resource.read"
    DELETE = "permission.document.resource.delete"
    WRITE = "permission.document.resource.write"
    SHARE = "permission.document.resource.share"


class DocumentRole(Enum):
    OWNER = (
        "role.document.owner",
        [
            DocumentPermission.READ,
            DocumentPermission.WRITE,
            DocumentPermission.DELETE,
            DocumentPermission.SHARE,
        ],
    )
    READER = ("role.document.reader", [DocumentPermission.READ])

    def name(self):
        return self.value[0]

    def permissions(self):
        return self.value[1]
    
    @classmethod
    def from_name(cls, v:str):
        for role in cls:
            if role.name() == v:
                return role 
        raise ValueError(f"{v} is not invalid DocumentRole")


def get_permissions_by_role(permission: DocumentPermission):
    return [role for role in DocumentRole if permission in role.permissions()]


class RoleAssignment(_BaseModel):
    role: str
    subject: str


class Document(BaseRootModel):
    owner_id: t.Optional[str] = Field(default=None)
    title: t.Optional[str] = Field(default=None)
    text_search: t.Optional[str] = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    file: t.Optional[FileMeta] = Field(default=None)
    thumbnail: t.Optional[FileMeta] = Field(default=None)
    removed: bool = Field(default=False)
    role_assignments: list[RoleAssignment] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def validate_role_assignments(cls, data: t.Any):
        if "owner_id" not in data:
            return data
        data["role_assignments"] = data.get(
            "role_assignments",
            [RoleAssignment(role=DocumentRole.OWNER.name(), subject=data["owner_id"]).model_dump()],
        )
        for ra in data["role_assignments"]:
            if ra["subject"] == data.get("owner_id"):
                return data
        data["role_assignments"] += [
            RoleAssignment(role=DocumentRole.OWNER.name(), subject=data["owner_id"]).model_dump()
        ]
        return data

    def check_permission(
        self, user: UserAccount, permission: DocumentPermission
    ) -> bool:
        for ra in self.role_assignments:
            if ra.subject == user.id:
                return permission in DocumentRole.from_name(ra.role).permissions()
        return False
