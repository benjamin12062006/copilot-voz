"""Biblioteca privada y acotada: guardar y retener se confirman juntos."""

from __future__ import annotations

import asyncio
import hashlib
import re
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4, uuid5, NAMESPACE_URL

from pydantic import BaseModel, ConfigDict, Field
from upstash_blob import AsyncBucket, BlobError
from starlette.concurrency import run_in_threadpool

from app.storage_preferences import StoragePreferences

from app.errors import ApiError, ErrorCode

DEFAULT_RETENTION_LIMIT = 20
MAX_DOCUMENTS = 100
MAX_WRITE_ATTEMPTS = 6
MAX_DOCUMENT_BYTES = 1_048_576


class Draft(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=200)
    format: Literal['markdown', 'text']
    content: str = Field(min_length=1, max_length=MAX_DOCUMENT_BYTES)


class UpdateDraft(Draft):
    revision: int = Field(ge=1)


class Document(Draft):
    id: str
    origin: Literal['web', 'agent']
    revision: int
    updatedAt: str
    wordCount: int
    fingerprint: str = ''
    blobId: UUID | None = None

    def public(self, summary: bool = False) -> dict:
        excluded = {'fingerprint', 'blobId'}
        if summary:
            excluded.add('content')
        return self.model_dump(exclude=excluded)


class RetiredFile(BaseModel):
    blobId: UUID
    format: Literal['markdown', 'text']


class Library(BaseModel):
    documents: list[Document] = Field(default_factory=list, max_length=MAX_DOCUMENTS)
    retentionLimit: int = Field(default=DEFAULT_RETENTION_LIMIT, ge=1, le=MAX_DOCUMENTS)
    pendingDeletes: list[RetiredFile] = Field(default_factory=list)


class DocumentStore:
    def __init__(self, bucket: AsyncBucket, namespace: str, max_bytes: int = MAX_DOCUMENT_BYTES,
                 preferences: StoragePreferences | None = None):
        self._bucket = bucket
        self._namespace = namespace.strip('/')
        self._max_bytes = max_bytes
        self._preferences = preferences

    async def list(self, owner: str) -> list[dict]:
        library, _ = await self._load(owner)
        return [document.public(summary=True) for document in reversed(library.documents)]

    async def get(self, owner: str, document_id: str) -> Document:
        library, _ = await self._load(owner)
        return find_document(library, document_id)

    async def save(self, owner: str, draft: Draft, *, document_id: str | None = None,
                   revision: int | None = None, idempotency_key: str | None = None) -> Document:
        validate_content(draft, self._max_bytes)
        await self._clean_retired(owner)
        staged_file = None
        is_update = document_id is not None
        fingerprint = hashlib.sha256(draft.model_dump_json().encode()).hexdigest()
        new_id = str(uuid4())
        if idempotency_key is not None:
            new_id = str(uuid5(NAMESPACE_URL, owner + ':' + idempotency_key))

        for attempt in range(MAX_WRITE_ATTEMPTS):
            library, etag = await self._load(owner)
            if is_update:
                current = find_document(library, document_id)
                if current.revision != revision:
                    await self._discard_staged(owner, staged_file, draft.format)
                    raise ApiError(ErrorCode.CONFLICT)
            else:
                current = next((doc for doc in library.documents if doc.id == new_id), None)
                if current is not None:
                    await self._discard_staged(owner, staged_file, draft.format)
                    if current.fingerprint != fingerprint:
                        raise ApiError(ErrorCode.CONFLICT)
                    return current

            if staged_file is None:
                staged_file = await self._write_file(owner, draft)
            saved = Document(**draft.model_dump(), id=document_id or new_id,
                             origin=current.origin if is_update else ('agent' if idempotency_key else 'web'),
                             revision=current.revision + 1 if is_update else 1,
                             updatedAt=datetime.now(UTC).isoformat(), wordCount=len(draft.content.split()),
                             fingerprint=fingerprint, blobId=staged_file)
            library.retentionLimit = await self._retention_limit(owner, library)
            previous_documents = library.documents
            library.documents = [doc for doc in library.documents if doc.id != saved.id]
            library.documents.append(saved)
            # El índice decide qué versiones siguen visibles; nunca se reutiliza un fileId.
            library.documents = library.documents[-library.retentionLimit:]
            visible_files = {doc.blobId for doc in library.documents}
            for old in previous_documents:
                if old.blobId is not None and old.blobId not in visible_files:
                    library.pendingDeletes.append(RetiredFile(blobId=old.blobId, format=old.format))
            if await self._commit(owner, library, etag):
                await self._clean_retired(owner)
                return saved
            await asyncio.sleep(0.01 * (attempt + 1))
        await self._discard_staged(owner, staged_file, draft.format)
        raise ApiError(ErrorCode.CONFLICT)

    async def preferences(self, owner: str) -> dict:
        library, _ = await self._load(owner)
        return {'retentionLimit': await self._retention_limit(owner, library)}

    async def set_retention(self, owner: str, limit: int) -> dict:
        if not 1 <= limit <= MAX_DOCUMENTS:
            raise ApiError(ErrorCode.INVALID_REQUEST)
        if self._preferences:
            await run_in_threadpool(self._preferences.set, owner, limit)
        await self._clean_retired(owner)
        for attempt in range(MAX_WRITE_ATTEMPTS):
            library, etag = await self._load(owner)
            if self._preferences:
                limit = await self._retention_limit(owner, library)
            retired = library.documents[:-limit]
            library.retentionLimit = limit
            library.documents = library.documents[-limit:]
            for document in retired:
                if document.blobId:
                    library.pendingDeletes.append(RetiredFile(blobId=document.blobId, format=document.format))
            if await self._commit(owner, library, etag):
                await self._clean_retired(owner)
                return {'retentionLimit': limit}
            await asyncio.sleep(0.01 * (attempt + 1))
        raise ApiError(ErrorCode.CONFLICT)

    async def delete(self, owner: str, document_id: str, revision: int) -> None:
        await self._clean_retired(owner)
        for attempt in range(MAX_WRITE_ATTEMPTS):
            library, etag = await self._load(owner)
            document = find_document(library, document_id)
            if document.revision != revision:
                raise ApiError(ErrorCode.CONFLICT)
            library.documents = [doc for doc in library.documents if doc.id != document_id]
            if document.blobId:
                library.pendingDeletes.append(RetiredFile(blobId=document.blobId, format=document.format))
            if await self._commit(owner, library, etag):
                await self._clean_retired(owner)
                return
            await asyncio.sleep(0.01 * (attempt + 1))
        raise ApiError(ErrorCode.CONFLICT)

    async def _retention_limit(self, owner: str, library: Library) -> int:
        if self._preferences is not None:
            return await run_in_threadpool(self._preferences.get, owner)
        return library.retentionLimit

    async def _load(self, owner: str) -> tuple[Library, str | None]:
        try:
            result = await self._bucket.get(self._path(owner))
            return Library.model_validate_json(result.content), result.etag
        except BlobError as error:
            if error.code == 'not_found':
                return Library(), None
            raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE) from None
        except ValueError:
            # Una biblioteca dañada nunca se interpreta como vacía para sobrescribirla.
            raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE) from None

    async def _commit(self, owner: str, library: Library, etag: str | None) -> bool:
        try:
            await self._bucket.put(self._path(owner), library.model_dump_json(),
                                   content_type='application/json', cache='no-store', multipart=False,
                                   allow_overwrite=etag is not None, if_unchanged=etag)
            return True
        except BlobError as error:
            if error.code in ('conflict', 'already_exists'):
                return False
            raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE) from None

    async def _write_file(self, owner: str, draft: Draft) -> UUID:
        file_id = uuid4()
        try:
            await self._bucket.put(self._file_path(owner, file_id, draft.format), draft.content,
                                   content_type='text/markdown; charset=utf-8' if draft.format == 'markdown' else 'text/plain; charset=utf-8',
                                   cache='no-store', allow_overwrite=False, multipart=False)
            return file_id
        except BlobError:
            raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE) from None

    async def _discard_staged(self, owner: str, file_id: UUID | None, format: str) -> None:
        if file_id is not None:
            await self._delete_files(owner, [RetiredFile(blobId=file_id, format=format)])

    async def _clean_retired(self, owner: str) -> None:
        for attempt in range(MAX_WRITE_ATTEMPTS):
            library, etag = await self._load(owner)
            if not library.pendingDeletes:
                return
            await self._delete_files(owner, library.pendingDeletes)
            library.pendingDeletes = []
            if await self._commit(owner, library, etag):
                return
            await asyncio.sleep(0.01 * (attempt + 1))
        raise ApiError(ErrorCode.CONFLICT)

    async def _delete_files(self, owner: str, files: list[RetiredFile]) -> None:
        paths = [self._file_path(owner, file.blobId, file.format) for file in files]
        try:
            await self._bucket.delete(paths)
        except BlobError:
            # El índice conserva pendientes: el reintento no necesita adivinar rutas.
            raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE) from None

    def _file_path(self, owner: str, file_id: UUID, format: str) -> str:
        if re.fullmatch(r'[A-Za-z0-9_-]+', owner) is None:
            raise ApiError(ErrorCode.INVALID_REQUEST)
        suffix = 'md' if format == 'markdown' else 'txt'
        return f'{self._namespace}/textos/{owner}/{file_id}.{suffix}'

    def _path(self, owner: str) -> str:
        owner_key = hashlib.sha256(owner.encode()).hexdigest()
        return f'{self._namespace}/libraries/{owner_key}.json'


def validate_content(draft: Draft, max_bytes: int) -> None:
    if not draft.title.strip() or not draft.content.strip():
        raise ApiError(ErrorCode.INVALID_REQUEST)
    try:
        size = len(draft.content.encode('utf-8'))
    except UnicodeError:
        raise ApiError(ErrorCode.INVALID_REQUEST) from None
    if size > max_bytes:
        raise ApiError(ErrorCode.TOO_LARGE)


def find_document(library: Library, document_id: str) -> Document:
    for document in library.documents:
        if document.id == document_id:
            return document
    raise ApiError(ErrorCode.NOT_FOUND)
