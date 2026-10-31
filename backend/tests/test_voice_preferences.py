"""La opción de lectura automática vive en Turso y es de cada usuario."""

import tempfile
import unittest
from pathlib import Path

import libsql
from fastapi.testclient import TestClient

from app.api import current_identity
from app.database import SqlUserRepository
from app.main import create_app
from app.migrations import apply_migrations
from app.settings import Settings
from app.users import UserIdentity, UserProfile
from app.voice_preferences import VoicePreferences


class VoicePreferencesAcceptance(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.connect = lambda: libsql.connect(str(Path(self.temporary.name) / 'voice.db'), isolation_level=None)
        apply_migrations(self.connect)
        self.users = SqlUserRepository(self.connect)
        self.preferences = VoicePreferences(self.connect)
        self.identity = UserIdentity('https://trusted.example', 'user_Owner')
        self.owner = self.users.provision(self.identity, UserProfile()).id
        self.other = self.users.provision(UserIdentity(self.identity.issuer, 'user_Other'), UserProfile()).id

    def test_mode_is_off_until_saved_and_belongs_to_each_user(self):
        self.assertEqual(self.preferences.auto_read_mode(self.owner), 'off')
        self.preferences.set_auto_read_mode(self.owner, 'agent')
        self.preferences.set_auto_read_mode(self.owner, 'all')
        self.assertEqual(self.preferences.auto_read_mode(self.owner), 'all')
        self.assertEqual(self.preferences.auto_read_mode(self.other), 'off')

    def test_routes_read_and_save_the_signed_in_user_mode(self):
        app = create_app(Settings(_env_file=None))
        with TestClient(app) as client:
            app.state.users = self.users
            app.state.voice_preferences = self.preferences
            self.assertEqual(client.get('/api/v1/voice/preferences').status_code, 401)

            app.dependency_overrides[current_identity] = lambda: self.identity
            self.assertEqual(client.get('/api/v1/voice/preferences').json(), {'autoReadMode': 'off'})
            saved = client.put('/api/v1/voice/preferences', json={'autoReadMode': 'agent'})
            self.assertEqual(saved.json(), {'autoReadMode': 'agent'})
            self.assertEqual(client.get('/api/v1/voice/preferences').json(), {'autoReadMode': 'agent'})
            self.assertEqual(self.preferences.auto_read_mode(self.other), 'off')

            invalid = client.put('/api/v1/voice/preferences', json={'autoReadMode': 'always'})
            self.assertEqual(invalid.status_code, 422)
            extra = client.put('/api/v1/voice/preferences', json={'autoReadMode': 'all', 'userId': self.other})
            self.assertEqual(extra.status_code, 422)


if __name__ == '__main__':
    unittest.main()
