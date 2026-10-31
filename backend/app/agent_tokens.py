"""Credenciales MCP personales: crear, comprobar y revocar en Turso."""

import hashlib
import re
import secrets
import time
from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from app.api import CurrentIdentity, Users
from app.database import ConnectionFactory, database_operation
from app.errors import ApiError, ErrorCode
from app.users import UserProfile

TOKEN_LIFETIME_SECONDS = 30 * 24 * 60 * 60
TOKEN_PATTERN = re.compile(r'^cp_mcp_([0-9a-f]{32})\.[A-Za-z0-9_-]{43}$')
TOKEN_COLUMNS = 'id, name, created_at, expires_at, revoked_at'
router = APIRouter(tags=['credenciales MCP'])


class TokenRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str = Field(default='MCP', min_length=1, max_length=80)


class AgentTokenRepository:
    def __init__(self, connect: ConnectionFactory):
        self._connect = connect

    def issue(self, owner: str, name: str) -> dict:
        token_id = uuid4().hex
        token = f'cp_mcp_{token_id}.{secrets.token_urlsafe(32)}'
        now = int(time.time())
        expires = now + TOKEN_LIFETIME_SECONDS
        with database_operation(self._connect) as connection:
            connection.execute('''
                INSERT INTO app_mcp_tokens
                    (id, user_id, token_hash, name, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (token_id, owner, token_digest(token), name, now, expires))
            connection.commit()
        return {'id': token_id, 'name': name, 'token': token,
                'createdAt': iso_date(now), 'expiresAt': iso_date(expires),
                'scope': 'documents:submit'}

    def list(self, owner: str) -> list[dict]:
        with database_operation(self._connect) as connection:
            rows = connection.execute(f'''
                SELECT {TOKEN_COLUMNS} FROM app_mcp_tokens
                WHERE user_id = ? ORDER BY created_at DESC, id
            ''', (owner,)).fetchall()
        return [{'id': row[0], 'name': row[1], 'createdAt': iso_date(row[2]),
                 'expiresAt': iso_date(row[3]),
                 'revokedAt': iso_date(row[4]) if row[4] is not None else None,
                 'scope': 'documents:submit'} for row in rows]

    def revoke(self, owner: str, token_id: str) -> None:
        with database_operation(self._connect) as connection:
            rows = connection.execute('''
                UPDATE app_mcp_tokens SET revoked_at = COALESCE(revoked_at, ?)
                WHERE id = ? AND user_id = ? RETURNING id
            ''', (int(time.time()), token_id, owner)).fetchall()
            if not rows:
                raise ApiError(ErrorCode.NOT_FOUND)
            connection.commit()

    def authenticate(self, token: str) -> str:
        match = TOKEN_PATTERN.fullmatch(token)
        if match is None:
            raise ApiError(ErrorCode.INVALID_SESSION)
        with database_operation(self._connect) as connection:
            row = connection.execute('''
                SELECT t.user_id, t.token_hash, t.expires_at, t.revoked_at
                FROM app_mcp_tokens AS t
                JOIN app_users AS u ON u.id = t.user_id
                WHERE t.id = ?
            ''', (match.group(1),)).fetchone()
        if row is None:
            raise ApiError(ErrorCode.INVALID_SESSION)
        matches_secret = secrets.compare_digest(row[1], token_digest(token))
        is_active = row[3] is None and row[2] > int(time.time())
        if not (matches_secret and is_active):
            raise ApiError(ErrorCode.INVALID_SESSION)
        return row[0]


def token_repository(request: Request) -> AgentTokenRepository:
    repository = request.app.state.agent_tokens
    if repository is None:
        raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE)
    return repository


Tokens = Annotated[AgentTokenRepository, Depends(token_repository)]


@router.post('/mcp/tokens', status_code=201)
def create_token(body: TokenRequest, identity: CurrentIdentity, users: Users,
                 tokens: Tokens, response: Response):
    owner = users.provision(identity, UserProfile()).id
    response.headers['Cache-Control'] = 'no-store'
    return tokens.issue(owner, body.name)


@router.get('/mcp/tokens')
def list_tokens(identity: CurrentIdentity, users: Users, tokens: Tokens, response: Response):
    user = users.find(identity)
    if user is None:
        raise ApiError(ErrorCode.NOT_FOUND)
    response.headers['Cache-Control'] = 'no-store'
    return {'items': tokens.list(user.id)}


@router.delete('/mcp/tokens/{token_id}', status_code=204)
def revoke_token(token_id: str, identity: CurrentIdentity, users: Users, tokens: Tokens):
    user = users.find(identity)
    if user is None:
        raise ApiError(ErrorCode.NOT_FOUND)
    tokens.revoke(user.id, token_id)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def iso_date(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, UTC).isoformat()
