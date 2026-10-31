"""Turso es la autoridad del límite de documentos de cada usuario."""

from app.database import ConnectionFactory, database_operation
from app.errors import ApiError, ErrorCode

DEFAULT_RETENTION_LIMIT = 20
MAX_RETENTION_LIMIT = 100


class StoragePreferences:
    def __init__(self, connect: ConnectionFactory):
        self._connect = connect

    def get(self, owner: str) -> int:
        with database_operation(self._connect) as connection:
            row = connection.execute(
                'SELECT retention_limit FROM app_storage_preferences WHERE user_id = ?',
                (owner,)).fetchone()
        return row[0] if row else DEFAULT_RETENTION_LIMIT

    def set(self, owner: str, limit: int) -> None:
        if not 1 <= limit <= MAX_RETENTION_LIMIT:
            raise ApiError(ErrorCode.INVALID_REQUEST)
        with database_operation(self._connect) as connection:
            connection.execute('''
                INSERT INTO app_storage_preferences (user_id, retention_limit) VALUES (?, ?)
                ON CONFLICT (user_id) DO UPDATE SET retention_limit = excluded.retention_limit
            ''', (owner, limit))
            connection.commit()
