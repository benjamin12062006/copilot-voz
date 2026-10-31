"""Tres rutas: identidad, lectura de perfil y creación idempotente."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.database import SqlUserRepository
from app.errors import ApiError, ErrorCode
from app.users import AppUser, UserIdentity, UserProfile

router = APIRouter(tags=["usuarios"])
bearer = HTTPBearer(auto_error=False)


class IdentityResponse(BaseModel):
    identity: UserIdentity


class UserResponse(BaseModel):
    user: AppUser


def current_identity(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> UserIdentity:
    if credentials is None:
        raise ApiError(ErrorCode.INVALID_SESSION)
    return request.app.state.authenticator.verify(credentials.credentials)


def user_repository(request: Request) -> SqlUserRepository:
    repository = request.app.state.users
    if repository is None:
        raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE)
    return repository


CurrentIdentity = Annotated[UserIdentity, Depends(current_identity)]
Users = Annotated[SqlUserRepository, Depends(user_repository)]


@router.get("/auth/me")
def read_identity(identity: CurrentIdentity) -> IdentityResponse:
    return IdentityResponse(identity=identity)


@router.get("/users/me")
def read_user(identity: CurrentIdentity, users: Users) -> UserResponse:
    user = users.find(identity)
    if user is None:
        raise ApiError(ErrorCode.NOT_FOUND)
    return UserResponse(user=user)


@router.put("/users/me")
def provision_user(identity: CurrentIdentity, users: Users) -> UserResponse:
    # El ID viene del token verificado. Email y nombre quedan vacíos en esta etapa.
    return UserResponse(user=users.provision(identity, UserProfile()))
