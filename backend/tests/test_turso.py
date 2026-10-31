"""Aceptación del repositorio y las migraciones, usando libSQL temporal real."""

import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from threading import Barrier

import jwt
import libsql
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.database import SqlUserRepository, TursoDatabase
from app.errors import ApiError, ErrorCode
from app.main import create_app
from app.migrations import MigrationError, apply_migrations, check_migrations
from app.settings import ConfigurationError, Feature, Settings
from app.users import UserIdentity, UserProfile


class TursoAcceptance(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.database_path = str(Path(self.temporary.name) / "copilot.db")
        self.repository = SqlUserRepository(self.connect)
        self.identity = UserIdentity("https://identity.example.test", "user_TestOwner")

    def connect(self):
        return libsql.connect(self.database_path, isolation_level=None)

    def test_migrate_repeat_and_check(self):
        self.assertTrue(apply_migrations(self.connect))
        self.assertFalse(apply_migrations(self.connect))
        check_migrations(self.connect)
        with closing(self.connect()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0], 3)

    def test_read_absent_and_provision_null_profile(self):
        apply_migrations(self.connect)
        self.assertIsNone(self.repository.find(self.identity))
        user = self.repository.provision(self.identity, UserProfile())
        self.assertEqual(self.repository.find(self.identity), user)
        response = user.model_dump(mode="json")
        self.assertEqual(set(response), {"id", "email", "displayName", "createdAt", "updatedAt"})
        self.assertIsNone(response["email"])
        self.assertIsNone(response["displayName"])
        self.assertTrue(response["createdAt"].endswith("Z"))

    def test_repeated_provision_preserves_profile_id_and_dates(self):
        apply_migrations(self.connect)
        first = self.repository.provision(self.identity, UserProfile("owner@example.test", "Owner"))
        second = self.repository.provision(self.identity, UserProfile("changed@example.test", "Changed"))
        self.assertEqual(first, second)

    def test_simultaneous_first_requests_share_id(self):
        apply_migrations(self.connect)
        barrier = Barrier(2, timeout=10)

        def provision(_):
            barrier.wait()
            return self.repository.provision(self.identity, UserProfile())

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(provision, range(2)))
        self.assertEqual(results[0], results[1])
        with closing(self.connect()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM app_users").fetchone()[0], 1)

    def test_sql_parameters_and_identity_isolation(self):
        apply_migrations(self.connect)
        identity = UserIdentity(self.identity.issuer, "user_'; DROP TABLE app_users; --")
        created = self.repository.provision(identity, UserProfile("a'b@example.test", "Name 'quoted'"))
        self.assertEqual(self.repository.find(identity), created)
        self.assertIsNone(self.repository.find(UserIdentity("https://other.example", identity.subject)))
        self.assertIsNone(self.repository.find(self.identity))
        check_migrations(self.connect)

    def test_provider_failure_exposes_no_diagnostics(self):
        def unavailable():
            raise RuntimeError("private provider diagnostics")

        with self.assertRaises(ApiError) as raised:
            SqlUserRepository(unavailable).find(self.identity)
        self.assertEqual(raised.exception.code, ErrorCode.PROVIDER_UNAVAILABLE)
        self.assertNotIn("private provider diagnostics", str(raised.exception))
        self.assertTrue(raised.exception.__suppress_context__)

    def test_schema_drift_and_checksum_mismatch_are_rejected(self):
        apply_migrations(self.connect)
        with closing(self.connect()) as connection:
            connection.execute("UPDATE schema_migrations SET checksum = 'incorrect'")
        with self.assertRaises(MigrationError):
            apply_migrations(self.connect)
        with closing(self.connect()) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM app_users").fetchone()[0], 0)

    def test_untracked_or_foreign_tables_are_not_adopted(self):
        with closing(self.connect()) as connection:
            connection.execute("CREATE TABLE app_users (id TEXT)")
        with self.assertRaises(MigrationError):
            apply_migrations(self.connect)
        with closing(self.connect()) as connection:
            tables = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            self.assertEqual(tables, [("app_users",)])
            connection.execute("CREATE TABLE unrelated (id INTEGER)")
        with self.assertRaises(MigrationError):
            apply_migrations(self.connect)

    def test_schema_is_verified_even_when_migration_is_recorded(self):
        apply_migrations(self.connect)
        with closing(self.connect()) as connection:
            connection.execute("ALTER TABLE app_users ADD COLUMN unexpected TEXT")
        with self.assertRaises(MigrationError):
            check_migrations(self.connect)

    def test_remote_configuration_requires_only_turso(self):
        settings = Settings(_env_file=None, TURSO_DATABASE_URL="libsql://copilot.example.turso.io", TURSO_AUTH_TOKEN="synthetic")
        self.assertEqual(settings.missing_for(Feature.USERS), [])
        TursoDatabase(settings)
        with self.assertRaises(ConfigurationError):
            TursoDatabase(Settings(_env_file=None))

    def test_http_token_and_profile_contracts(self):
        apply_migrations(self.connect)
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()
        settings = Settings(
            _env_file=None,
            CLERK_ISSUER=self.identity.issuer,
            CLERK_JWT_KEY=public_key,
            COPILOT_ALLOWED_CLERK_USER_IDS=[self.identity.subject],
        )
        app = create_app(settings)

        def token(changes=None):
            now = int(time.time())
            claims = {
                "iss": self.identity.issuer, "sub": self.identity.subject,
                "sid": "sess_TestSession", "azp": "http://localhost:3000",
                "exp": now + 120, "nbf": now - 1, "iat": now - 1,
            }
            claims.update(changes or {})
            return jwt.encode(claims, private_key, algorithm="RS256")

        def headers(changes=None):
            return {"Authorization": f"Bearer {token(changes)}"}

        with TestClient(app) as client:
            app.state.users = self.repository
            self.assertEqual(client.get("/health").json(), {"status": "ok"})
            self.assertEqual(client.get("/api/v1/auth/me").status_code, 401)
            self.assertEqual(client.get("/api/v1/auth/me", headers=headers()).json(), {
                "identity": {"issuer": self.identity.issuer, "subject": self.identity.subject}
            })
            for changes in (
                {"iss": "https://other.example"}, {"azp": "https://other.example"},
                {"exp": int(time.time()) - 60}, {"nbf": int(time.time()) + 600},
                {"sts": "pending"}, {"sid": ""}, {"sub": ""},
            ):
                with self.subTest(changes=changes):
                    self.assertEqual(client.get("/api/v1/auth/me", headers=headers(changes)).status_code, 401)
            self.assertEqual(client.get("/api/v1/auth/me", headers=headers({"sub": "user_Other"})).status_code, 403)
            self.assertEqual(client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"}).status_code, 401)
            other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            signed_claims = jwt.decode(token(), public_key, algorithms=["RS256"], options={"verify_aud": False})
            wrong_signature = jwt.encode(signed_claims, other_key, algorithm="RS256")
            self.assertEqual(client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {wrong_signature}"}).status_code, 401)
            self.assertEqual(client.get("/api/v1/auth/me", headers={"Cookie": f"__session={token()}"}).status_code, 401)
            self.assertEqual(client.get("/api/v1/users/me", headers=headers()).status_code, 404)
            first = client.put("/api/v1/users/me", headers=headers(), json={"subject": "user_Attacker"})
            self.assertEqual(first.status_code, 200)
            self.assertEqual(client.put("/api/v1/users/me", headers=headers()).json(), first.json())
            self.assertEqual(client.get("/api/v1/users/me", headers=headers()).json(), first.json())
            self.assertIsNone(self.repository.find(UserIdentity(self.identity.issuer, "user_Attacker")))
            app.state.users = None
            unavailable = client.get("/api/v1/users/me", headers=headers())
            self.assertEqual(unavailable.status_code, 503)
            self.assertEqual(unavailable.json()["error"]["requestId"], unavailable.headers["X-Request-ID"])


if __name__ == "__main__":
    unittest.main()
