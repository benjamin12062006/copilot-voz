"""La identidad de Clerk emite credenciales; Turso autoriza cada envío MCP."""

import hashlib
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import libsql
from fastapi.testclient import TestClient

from app.agent_tokens import AgentTokenRepository
from app.api import current_identity
from app.database import SqlUserRepository
from app.errors import ApiError, ErrorCode
from app.main import create_app
from app.migrations import apply_migrations, check_migrations, MIGRATION_FILE, CREATE_MIGRATIONS
from app.settings import Settings
from app.users import UserIdentity, UserProfile


class TokenAcceptance(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.connect = lambda: libsql.connect(str(Path(self.temporary.name) / 'api.db'), isolation_level=None)
        apply_migrations(self.connect)
        self.users = SqlUserRepository(self.connect)
        self.tokens = AgentTokenRepository(self.connect)
        self.identity = UserIdentity('https://trusted.example', 'user_Owner')
        self.owner = self.users.provision(self.identity, UserProfile()).id
        self.other = self.users.provision(UserIdentity(self.identity.issuer, 'user_Other'), UserProfile()).id

    def test_only_hash_is_stored_and_token_is_bound_to_owner(self):
        issued = self.tokens.issue(self.owner, 'Codex')
        self.assertEqual(self.tokens.authenticate(issued['token']), self.owner)
        with closing(self.connect()) as db:
            stored = db.execute('SELECT token_hash FROM app_mcp_tokens').fetchone()[0]
        self.assertEqual(stored, hashlib.sha256(issued['token'].encode()).hexdigest())
        self.assertNotIn(issued['token'], str(self.tokens.list(self.owner)))
        self.assertNotIn(stored, str(self.tokens.list(self.owner)))
        self.assertEqual(self.tokens.list(self.other), [])

    def test_invalid_expired_revoked_and_missing_users_are_denied(self):
        issued = self.tokens.issue(self.owner, 'Codex')
        for invalid in ('invalid', 'Bearer token', issued['token'][:-1] + '!',
                        issued['token'][:-1] + ('A' if issued['token'][-1] != 'A' else 'B')):
            with self.assertRaises(ApiError):
                self.tokens.authenticate(invalid)
        with patch('app.agent_tokens.time.time', return_value=time.time() + 31 * 86400):
            with self.assertRaises(ApiError):
                self.tokens.authenticate(issued['token'])
        with self.assertRaises(ApiError) as error:
            self.tokens.revoke(self.other, issued['id'])
        self.assertEqual(error.exception.code, ErrorCode.NOT_FOUND)
        self.tokens.revoke(self.owner, issued['id'])
        self.tokens.revoke(self.owner, issued['id'])
        with self.assertRaises(ApiError):
            self.tokens.authenticate(issued['token'])
        another = self.tokens.issue(self.owner, 'Other')['token']
        with closing(self.connect()) as db:
            # Simular una importación externa que deja una credencial huérfana.
            db.execute('PRAGMA foreign_keys = OFF')
            db.execute('DELETE FROM app_users WHERE id = ?', (self.owner,))
        with self.assertRaises(ApiError):
            self.tokens.authenticate(another)

    def test_http_creation_listing_revocation_and_no_owner_in_body(self):
        app = create_app(Settings(_env_file=None))
        with TestClient(app) as client:
            app.state.users = self.users
            app.state.agent_tokens = self.tokens
            self.assertEqual(client.post('/api/v1/mcp/tokens', json={}).status_code, 401)
            app.dependency_overrides[current_identity] = lambda: self.identity
            forbidden = client.post('/api/v1/mcp/tokens', json={'userId': self.other})
            self.assertEqual(forbidden.status_code, 422)
            response = client.post('/api/v1/mcp/tokens', json={'name': 'Codex'})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.headers['cache-control'], 'no-store')
            issued = response.json()
            self.assertEqual(self.tokens.authenticate(issued['token']), self.owner)
            self.assertNotIn(issued['token'], client.get('/api/v1/mcp/tokens').text)
            self.assertEqual(client.delete('/api/v1/mcp/tokens/'+issued['id']).status_code, 204)
            with self.assertRaises(ApiError):
                self.tokens.authenticate(issued['token'])

    def test_mcp_token_cannot_be_used_as_a_web_session(self):
        token = self.tokens.issue(self.owner, 'Codex')['token']
        app = create_app(Settings(_env_file=None, CLERK_ISSUER='https://trusted.example', CLERK_JWT_KEY='invalid'))
        with TestClient(app) as client:
            self.assertEqual(client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer '+token}).status_code, 401)

    def test_upgrade_from_v1_preserves_existing_user(self):
        other_path = str(Path(self.temporary.name) / 'upgrade.db')
        connect = lambda: libsql.connect(other_path, isolation_level=None)
        with closing(connect()) as db:
            db.execute(CREATE_MIGRATIONS)
            db.execute(MIGRATION_FILE.read_text())
            db.execute('INSERT INTO schema_migrations VALUES (?, ?, ?, ?)',
                       (1, MIGRATION_FILE.stem, hashlib.sha256(MIGRATION_FILE.read_bytes()).hexdigest(), '2026-10-31'))
        repository = SqlUserRepository(connect)
        original = repository.provision(self.identity, UserProfile())
        self.assertTrue(apply_migrations(connect))
        check_migrations(connect)
        self.assertEqual(repository.find(self.identity), original)
        self.assertFalse(apply_migrations(connect))


class McpTransportAcceptance(unittest.TestCase):
    def test_private_token_is_not_sent_over_remote_http(self):
        from app.mcp_server import validate_api_url
        for url in ('http://remote.example/api/v1', 'https://user:secret@example.test/api/v1', 'https://example.test/?token=secret'):
            with self.assertRaises(ValueError):
                validate_api_url(url)
        validate_api_url('https://api.example.test/api/v1')
        validate_api_url('http://127.0.0.1:8000/api/v1')
