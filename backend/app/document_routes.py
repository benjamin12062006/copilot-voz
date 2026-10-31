"""Entradas HTTP de biblioteca y envío limitado desde el agente."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app.api import CurrentIdentity, Users, bearer
from app.documents import Draft, UpdateDraft, DocumentStore
from app.errors import ApiError, ErrorCode
from app.prepare_document import prepare
from app.agent_tokens import Tokens

router = APIRouter(tags=['documentos'])


def document_store(request: Request) -> DocumentStore:
    if request.app.state.documents is None:
        raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE)
    return request.app.state.documents


Store = Annotated[DocumentStore, Depends(document_store)]


def owner_id(identity: CurrentIdentity, users: Users) -> str:
    user = users.find(identity)
    if user is None:
        raise ApiError(ErrorCode.NOT_FOUND)
    return user.id


Owner = Annotated[str, Depends(owner_id)]


@router.get('/documents')
async def list_documents(owner: Owner, store: Store):
    return {'items': await store.list(owner), 'nextCursor': None}


@router.post('/documents', status_code=201)
async def create_document(draft: Draft, owner: Owner, store: Store):
    return {'document': (await store.save(owner, draft)).public()}


@router.get('/documents/{document_id}')
async def read_document(document_id: str, owner: Owner, store: Store):
    return {'document': (await store.get(owner, document_id)).public()}


@router.put('/documents/{document_id}')
async def update_document(document_id: str, draft: UpdateDraft, owner: Owner, store: Store):
    content = Draft(**draft.model_dump(exclude={'revision'}))
    saved = await store.save(owner, content, document_id=document_id, revision=draft.revision)
    return {'document': saved.public()}


class AgentSubmission(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    markdown: str = Field(min_length=1, max_length=1_048_576)
    idempotencyKey: str = Field(min_length=1, max_length=128)


def agent_owner(tokens: Tokens, credentials=Depends(bearer)) -> str:
    if credentials is None:
        raise ApiError(ErrorCode.INVALID_SESSION)
    return tokens.authenticate(credentials.credentials)


@router.post('/agent/documents')
async def submit_markdown(body: AgentSubmission, store: Store, owner: Annotated[str, Depends(agent_owner)]):
    document = await store.save(owner, Draft(title=body.title, format='markdown', content=body.markdown),
                                idempotency_key=body.idempotencyKey)
    return {'documentId': document.id, 'revision': document.revision}


@router.get('/documents/{document_id}/prepared')
async def prepared_document(document_id: str, revision: int, owner: Owner, store: Store):
    document = await store.get(owner, document_id)
    if document.revision != revision:
        raise ApiError(ErrorCode.CONFLICT)
    return {'prepared': await run_in_threadpool(prepare, document)}


class RetentionPreference(BaseModel):
    retentionLimit: int = Field(ge=1, le=100)


@router.get('/storage/preferences')
async def storage_preferences(owner: Owner, store: Store):
    return await store.preferences(owner)


@router.put('/storage/preferences')
async def update_storage_preferences(body: RetentionPreference, owner: Owner, store: Store):
    return await store.set_retention(owner, body.retentionLimit)


@router.delete('/documents/{document_id}', status_code=204)
async def delete_document(document_id: str, revision: int, owner: Owner, store: Store):
    await store.delete(owner, document_id, revision)
