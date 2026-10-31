"""Migración manual: nunca se ejecuta al importar ni al arrancar FastAPI.

Desde backend/: uv run --locked python -m app.migrations [--apply]
Sin --apply solo comprueba el esquema; no crea tablas ni registros.
"""

import argparse
import hashlib
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from app.database import Connection, ConnectionFactory, TursoDatabase
from app.settings import ConfigurationError, load_settings

MIGRATION_FILE: Final = Path(__file__).resolve().parents[1] / "migrations/001_app_users.sql"
EXPECTED_USER_COLUMNS: Final = [
    ("id", "TEXT", 1, 1),
    ("identity_issuer", "TEXT", 1, 0),
    ("identity_subject", "TEXT", 1, 0),
    ("email", "TEXT", 0, 0),
    ("display_name", "TEXT", 0, 0),
    ("created_at", "TEXT", 1, 0),
    ("updated_at", "TEXT", 1, 0),
]

CREATE_MIGRATIONS: Final = """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        checksum TEXT NOT NULL,
        applied_at TEXT NOT NULL
    )
"""


MIGRATION_FILES: Final = [MIGRATION_FILE, MIGRATION_FILE.with_name('002_mcp_tokens.sql'),
                         MIGRATION_FILE.with_name('003_storage_preferences.sql'),
                         MIGRATION_FILE.with_name('004_voice_preferences.sql')]


class MigrationError(RuntimeError):
    pass


def apply_migrations(connect: ConnectionFactory) -> bool:
    with closing(connect()) as connection:
        try:
            connection.execute("BEGIN IMMEDIATE")
            tables = user_tables(connection)
            require_copilot_tables(tables)
            connection.execute(CREATE_MIGRATIONS)
            applied = verified_history(connection)
            if 'app_users' in tables and 1 not in applied:
                raise MigrationError('app_users existe sin migración registrada.')
            if 'app_mcp_tokens' in tables and 2 not in applied:
                raise MigrationError('app_mcp_tokens existe sin migración registrada.')
            if 'app_storage_preferences' in tables and 3 not in applied:
                raise MigrationError('app_storage_preferences existe sin migración registrada.')
            if 'app_voice_preferences' in tables and 4 not in applied:
                raise MigrationError('app_voice_preferences existe sin migración registrada.')
            for version, path in enumerate(MIGRATION_FILES, 1):
                if version in applied:
                    continue
                connection.execute(path.read_text())
                verify_users_schema(connection)
                if version >= 2:
                    verify_tokens_schema(connection)
                if version >= 3:
                    verify_preferences_schema(connection)
                if version >= 4:
                    verify_voice_preferences_schema(connection)
                connection.execute(
                    'INSERT INTO schema_migrations (version, name, checksum, applied_at) VALUES (?, ?, ?, ?)',
                    (version, path.stem, hashlib.sha256(path.read_bytes()).hexdigest(), datetime.now(UTC).isoformat()))
            verify_users_schema(connection)
            verify_tokens_schema(connection)
            verify_preferences_schema(connection)
            verify_voice_preferences_schema(connection)
            connection.commit()
            return len(applied) < len(MIGRATION_FILES)
        except Exception:
            connection.rollback()
            raise


def check_migrations(connect: ConnectionFactory) -> None:
    with closing(connect()) as connection:
        tables = user_tables(connection)
        require_copilot_tables(tables)
        if 'schema_migrations' not in tables or len(verified_history(connection)) != len(MIGRATION_FILES):
            raise MigrationError('Faltan migraciones de Copilot.')
        verify_users_schema(connection)
        verify_tokens_schema(connection)
        verify_preferences_schema(connection)
        verify_voice_preferences_schema(connection)


def verified_history(connection: Connection) -> set[int]:
    rows = connection.execute('SELECT version, name, checksum FROM schema_migrations ORDER BY version').fetchall()
    expected = [(number, path.stem, hashlib.sha256(path.read_bytes()).hexdigest())
                for number, path in enumerate(MIGRATION_FILES, 1)]
    if rows != expected[:len(rows)]:
        raise MigrationError('El historial de migraciones no coincide con los archivos SQL.')
    return {row[0] for row in rows}


def verify_tokens_schema(connection: Connection) -> None:
    rows = connection.execute('PRAGMA table_info(app_mcp_tokens)').fetchall()
    actual = [(row[1], row[2].upper(), row[3], row[5]) for row in rows]
    expected = [('id', 'TEXT', 1, 1), ('user_id', 'TEXT', 1, 0),
                ('token_hash', 'TEXT', 1, 0), ('name', 'TEXT', 1, 0),
                ('created_at', 'INTEGER', 1, 0), ('expires_at', 'INTEGER', 1, 0),
                ('revoked_at', 'INTEGER', 0, 0)]
    if actual != expected:
        raise MigrationError('El esquema de tokens MCP no coincide con la migración 002.')


def verify_preferences_schema(connection: Connection) -> None:
    rows = connection.execute('PRAGMA table_info(app_storage_preferences)').fetchall()
    columns = [(row[1], row[2].upper(), row[3], row[5]) for row in rows]
    if columns != [('user_id', 'TEXT', 1, 1), ('retention_limit', 'INTEGER', 1, 0)]:
        raise MigrationError('El esquema de preferencias no coincide con la migración 003.')


def verify_voice_preferences_schema(connection: Connection) -> None:
    rows = connection.execute('PRAGMA table_info(app_voice_preferences)').fetchall()
    columns = [(row[1], row[2].upper(), row[3], row[5]) for row in rows]
    if columns != [('user_id', 'TEXT', 1, 1), ('auto_read_mode', 'TEXT', 1, 0)]:
        raise MigrationError('El esquema de preferencias de voz no coincide con la migración 004.')


def user_tables(connection: Connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT GLOB 'sqlite_*'"
    ).fetchall()
    return {row[0] for row in rows}


def require_copilot_tables(tables: set[str]) -> None:
    if tables - {"app_users", "schema_migrations", "app_mcp_tokens", "app_storage_preferences",
                 "app_voice_preferences"}:
        raise MigrationError("La base contiene tablas ajenas; usar una base exclusiva de Copilot.")


def verify_users_schema(connection: Connection) -> None:
    rows = connection.execute("PRAGMA table_info(app_users)").fetchall()
    columns = [(row[1], row[2].upper(), row[3], row[5]) for row in rows]
    if columns != EXPECTED_USER_COLUMNS:
        raise MigrationError("El esquema app_users no coincide con la migración 001.")
    if not has_unique_identity(connection):
        raise MigrationError("Falta la restricción única de issuer/subject.")


def has_unique_identity(connection: Connection) -> bool:
    for index in connection.execute("PRAGMA index_list(app_users)").fetchall():
        is_complete_unique_index = index[2] == 1 and index[4] == 0
        if not is_complete_unique_index:
            continue
        quoted_name = '"' + index[1].replace('"', '""') + '"'
        columns = connection.execute(f"PRAGMA index_info({quoted_name})").fetchall()
        if [column[2] for column in columns] == ["identity_issuer", "identity_subject"]:
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Migraciones de la base exclusiva de Copilot")
    parser.add_argument("--apply", action="store_true", help="aplicar SQL transaccional no destructivo")
    arguments = parser.parse_args()
    try:
        database = TursoDatabase(load_settings())
        if arguments.apply:
            changed = apply_migrations(database.connect)
            print("Migraciones aplicadas." if changed else "Migraciones ya aplicadas y verificadas.")
        else:
            check_migrations(database.connect)
            print("Esquema y migraciones verificados.")
        return 0
    except (ConfigurationError, MigrationError) as error:
        print(str(error))
        return 1
    except Exception:
        print("No se pudo comprobar o migrar Turso. Revisar conexión y credenciales del backend.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
