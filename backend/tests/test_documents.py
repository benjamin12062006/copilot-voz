import asyncio
import json
import unittest
from types import SimpleNamespace

from upstash_blob import BlobError

from app.documents import DocumentStore, Draft
from app.errors import ApiError, ErrorCode
from app.prepare_document import prepare
from app.mcp_server import mcp


class MemoryBucket:
    def __init__(self):
        self.objects = {}
        self.version = 0

    async def get(self, path):
        await asyncio.sleep(0)
        if path not in self.objects:
            raise BlobError('not_found')
        content, etag = self.objects[path]
        return SimpleNamespace(content=content.encode(), etag=etag)

    async def delete(self, paths):
        for path in paths:
            self.objects.pop(path, None)

    async def put(self, path, body, **options):
        await asyncio.sleep(0)
        existing = self.objects.get(path)
        if existing and (not options['allow_overwrite'] or existing[1] != options['if_unchanged']):
            raise BlobError('conflict')
        self.version += 1
        self.objects[path] = body, str(self.version)


class DocumentsAcceptance(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bucket = MemoryBucket()
        self.store = DocumentStore(self.bucket, 'test')
        self.draft = Draft(title='Título', format='markdown', content='# Hola\r\n\nTexto áé.')

    async def test_retains_last_twenty_and_removes_content(self):
        first = await self.store.save('owner', self.draft)
        for index in range(20):
            await self.store.save('owner', Draft(title=str(index), format='markdown', content=str(index)))
        self.assertEqual(len(await self.store.list('owner')), 20)
        with self.assertRaises(ApiError):
            await self.store.get('owner', first.id)
        self.assertNotIn('Texto áé.', next(iter(self.bucket.objects.values()))[0])
        self.assertEqual(await self.store.list('other'), [])

    async def test_update_conflict_and_original(self):
        doc = await self.store.save('owner', self.draft)
        self.assertEqual((await self.store.get('owner', doc.id)).content, self.draft.content)
        updated = await self.store.save('owner', self.draft, document_id=doc.id, revision=1)
        self.assertEqual(updated.revision, 2)
        with self.assertRaises(ApiError) as error:
            await self.store.save('owner', self.draft, document_id=doc.id, revision=1)
        self.assertEqual(error.exception.code, ErrorCode.CONFLICT)

    async def test_concurrent_idempotency_and_restart(self):
        results = await asyncio.gather(*[self.store.save('owner', self.draft, idempotency_key='same') for _ in range(4)])
        self.assertEqual(len({doc.id for doc in results}), 1)
        restarted = DocumentStore(self.bucket, 'test')
        self.assertEqual((await restarted.save('owner', self.draft, idempotency_key='same')).id, results[0].id)
        changed = Draft(title='Other', format='markdown', content='Changed')
        with self.assertRaises(ApiError):
            await restarted.save('owner', changed, idempotency_key='same')

    async def test_concurrent_distinct_writes_are_not_lost(self):
        await asyncio.gather(*[self.store.save('owner', self.draft) for _ in range(4)])
        self.assertEqual(len(await self.store.list('owner')), 4)

    async def test_empty_and_utf8_limit(self):
        for content in ('  ', 'é' * 600_000):
            with self.assertRaises(ApiError):
                await self.store.save('owner', Draft(title='Title', format='markdown', content=content))
        self.assertEqual(self.bucket.objects, {})

    async def test_markdown_and_plain_text_preparation(self):
        draft = Draft(title='Test', format='markdown', content='# Título\n\n**Hola** [mundo](https://example.test)\n\n```py\nsecret_code\n```\n\n| A | B |\n| - | - |\n| 1 | 2 |')
        result = prepare(await self.store.save('owner', draft))
        self.assertIn('Hola mundo', result['spokenText'])
        self.assertNotIn('secret_code', result['spokenText'])
        self.assertIn('A: 1', result['spokenText'])
        plain = Draft(title='Text', format='text', content='C# a*b #etiqueta')
        self.assertEqual(prepare(await self.store.save('owner', plain))['spokenText'], plain.content)

    async def test_mcp_exposes_only_submission(self):
        tools = await mcp.list_tools()
        self.assertEqual([tool.name for tool in tools], ['voice_submit_document'])

    async def test_agent_http_and_mcp_share_storage(self):
        import hashlib
        import os
        from unittest.mock import patch
        import httpx
        from app.main import create_app
        from app.settings import Settings
        from app.document_routes import owner_id
        from app.mcp_server import voice_submit_document

        import tempfile
        from pathlib import Path
        import libsql
        from app.database import SqlUserRepository
        from app.users import UserIdentity, UserProfile
        from app.agent_tokens import AgentTokenRepository
        from app.migrations import apply_migrations
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        connect = lambda: libsql.connect(str(Path(temporary.name) / 'tokens.db'), isolation_level=None)
        apply_migrations(connect)
        owner = SqlUserRepository(connect).provision(UserIdentity('issuer', 'user_Test'), UserProfile()).id
        tokens = AgentTokenRepository(connect)
        token = tokens.issue(owner, 'Test')['token']
        app = create_app(Settings(_env_file=None))
        app.state.agent_tokens = tokens
        app.state.documents = self.store
        app.dependency_overrides[owner_id] = lambda: owner
        original_client = httpx.AsyncClient
        transport = httpx.ASGITransport(app=app)
        def client_factory(**kwargs):
            return original_client(transport=transport, **kwargs)
        with patch.dict(os.environ, {'COPILOT_API_BASE_URL': 'http://127.0.0.1/api/v1',
                                    'COPILOT_MCP_API_TOKEN': token}):
            with patch('app.mcp_server.httpx.AsyncClient', side_effect=client_factory):
                saved = await voice_submit_document('Desde IA', '# Markdown', 'request-1')
                again = await voice_submit_document('Desde IA', '# Markdown', 'request-1')
        self.assertEqual(saved, again)
        async with original_client(transport=transport, base_url='http://127.0.0.1') as client:
            response = await client.get('/api/v1/documents')
            self.assertEqual(response.json()['items'][0]['origin'], 'agent')
            result = await client.get('/api/v1/documents/'+saved['documentId'])
            self.assertEqual(result.json()['document']['content'], '# Markdown')
            forbidden = await client.post('/api/v1/agent/documents', headers={'Authorization': 'Bearer wrong'},
                    json={'title': 'Bad', 'markdown': 'x', 'idempotencyKey': 'bad'})
            self.assertEqual(forbidden.status_code, 401)
            prepared = await client.get('/api/v1/documents/'+saved['documentId']+'/prepared?revision=1')
            self.assertEqual(prepared.json()['prepared']['spokenText'], 'Markdown')

    async def test_private_files_are_removed_after_twenty_and_on_edit(self):
        first = await self.store.save('owner', self.draft)
        path = f'test/textos/owner/{first.blobId}.md'
        self.assertEqual(self.bucket.objects[path][0], self.draft.content)
        updated = await self.store.save('owner', self.draft, document_id=first.id, revision=1)
        self.assertNotEqual(updated.blobId, first.blobId)
        self.assertNotIn(path, self.bucket.objects)
        for _ in range(20):
            await self.store.save('owner', self.draft)
        paths = [key for key in self.bucket.objects if '/textos/owner/' in key]
        self.assertEqual(len(paths), 20)
        self.assertNotIn('blobId', updated.public())

    async def test_failed_retention_is_durable_and_retried(self):
        for _ in range(20):
            await self.store.save('owner', self.draft)
        original_delete = self.bucket.delete
        async def fail(paths):
            raise BlobError('request_failed')
        self.bucket.delete = fail
        with self.assertRaises(ApiError):
            await self.store.save('owner', self.draft, idempotency_key='last')
        library, _ = await self.store._load('owner')
        self.assertTrue(library.pendingDeletes)
        self.bucket.delete = original_delete
        restarted = DocumentStore(self.bucket, 'test')
        await restarted.save('owner', self.draft, idempotency_key='last')
        paths = [key for key in self.bucket.objects if '/textos/owner/' in key]
        self.assertEqual(len(paths), 20)
        self.assertFalse((await restarted._load('owner'))[0].pendingDeletes)

    async def test_manual_delete_checks_owner_and_revision(self):
        document = await self.store.save('owner', self.draft)
        with self.assertRaises(ApiError):
            await self.store.delete('other', document.id, 1)
        with self.assertRaises(ApiError) as conflict:
            await self.store.delete('owner', document.id, 2)
        self.assertEqual(conflict.exception.code, ErrorCode.CONFLICT)
        await self.store.delete('owner', document.id, 1)
        self.assertEqual(await self.store.list('owner'), [])
        self.assertFalse([key for key in self.bucket.objects if '/textos/owner/' in key])

    async def test_retention_is_persisted_in_turso_and_applied_to_agent(self):
        import tempfile
        from pathlib import Path
        import libsql
        from app.storage_preferences import StoragePreferences
        from app.migrations import apply_migrations
        from app.database import SqlUserRepository
        from app.users import UserIdentity, UserProfile
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        connect = lambda: libsql.connect(str(Path(temporary.name)/'limits.db'), isolation_level=None)
        apply_migrations(connect)
        owner = SqlUserRepository(connect).provision(UserIdentity('issuer', 'user_Limit'), UserProfile()).id
        preferences = StoragePreferences(connect)
        store = DocumentStore(self.bucket, 'test', preferences=preferences)
        self.assertEqual((await store.preferences(owner))['retentionLimit'], 20)
        await store.set_retention(owner, 3)
        for index in range(5):
            await store.save(owner, self.draft, idempotency_key=str(index))
        self.assertEqual(len(await store.list(owner)), 3)
        restarted = DocumentStore(self.bucket, 'test', preferences=StoragePreferences(connect))
        self.assertEqual((await restarted.preferences(owner))['retentionLimit'], 3)
        await restarted.set_retention(owner, 1)
        self.assertEqual(len(await restarted.list(owner)), 1)
        self.assertEqual(preferences.get(owner), 1)
        with self.assertRaises(ApiError):
            await restarted.set_retention(owner, 0)
