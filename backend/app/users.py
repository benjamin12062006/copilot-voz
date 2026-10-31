"""Datos de usuarios independientes del proveedor de identidad y del transporte."""

from dataclasses import dataclass

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


@dataclass(frozen=True)
class UserIdentity:
    issuer: str
    subject: str


@dataclass(frozen=True)
class UserProfile:
    email: str | None = None
    display_name: str | None = None


class AppUser(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    email: str | None
    display_name: str | None = Field(alias="displayName")
    created_at: AwareDatetime = Field(alias="createdAt")
    updated_at: AwareDatetime = Field(alias="updatedAt")
