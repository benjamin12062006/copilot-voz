"""Conexiones remotas libSQL y repositorio de perfiles con SQL parametrizado."""

from collections.abc import Callable, Iterator
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from typing import Final
from uuid import uuid4

import libsql

from app.errors import ApiError, ErrorCode
from app.settings import ConfigurationError, Feature, Settings, load_settings
from app.users import AppUser, UserIdentity, UserProfile

USER_COLUMNS: Final = """
    id,
    email,
    display_name,
    created_at,
    updated_at
"""

FIND_USER: Final = f"""
    SELECT {USER_COLUMNS}
    FROM app_users
    WHERE identity_issuer = ? AND identity_subject = ?
"""

CREATE_USER: Final = f"""
    INSERT INTO app_users (
        id,
        identity_issuer,
        identity_subject,
        email,
        display_name,
        created_at,
        updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT (identity_issuer, identity_subject)
    DO UPDATE SET identity_subject = excluded.identity_subject
    RETURNING {USER_COLUMNS}
"""


Connection = libsql.Connection
ConnectionFactory = Callable[[], Connection]


class TursoDatabase:
    def __init__(self, settings: Settings) -> None:
        settings.require(Feature.USERS)
        self._url = settings.turso_database_url
        self._token = settings.turso_auth_token

    def connect(self) -> Connection:
        # Cada operación usa su conexión: no compartir una transacción entre threads.
        return libsql.connect(
            database=self._url,
            auth_token=self._token.get_secret_value(),
            isolation_level=None,
        )

    def check_connection(self) -> None:
        with database_operation(self.connect) as connection:
            row = connection.execute("SELECT 1").fetchone()
            if row != (1,):
                raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE)


class SqlUserRepository:
    def __init__(self, connect: ConnectionFactory) -> None:
        self._connect = connect

    def find(self, identity: UserIdentity) -> AppUser | None:
        with database_operation(self._connect) as connection:
            row = connection.execute(FIND_USER, (identity.issuer, identity.subject)).fetchone()
            return user_from_row(row) if row is not None else None

    def provision(self, identity: UserIdentity, profile: UserProfile) -> AppUser:
        with database_operation(self._connect) as connection:
            now = datetime.now(UTC).isoformat()
            rows = connection.execute(
                CREATE_USER,
                (
                    str(uuid4()),
                    identity.issuer,
                    identity.subject,
                    profile.email,
                    profile.display_name,
                    now,
                    now,
                ),
            ).fetchall()
            # Un solo statement es una transacción atómica: el conflicto devuelve
            # la fila ganadora sin cambiar perfil, ID ni fechas. Consumir RETURNING
            # completa la escritura antes de devolver el resultado al cliente.
            if len(rows) != 1:
                raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE)
            connection.commit()
            return user_from_row(rows[0])


@contextmanager
def database_operation(connect: ConnectionFactory) -> Iterator[Connection]:
    try:
        with closing(connect()) as connection:
            yield connection
    except ApiError:
        raise
    except Exception:
        # El driver nativo no ofrece una jerarquía DB-API uniforme en cada versión.
        # La frontera limita el error a esta operación y nunca devuelve SQL o tokens.
        raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE) from None


def user_from_row(row: tuple) -> AppUser:
    return AppUser(
        id=row[0],
        email=row[1],
        display_name=row[2],
        created_at=row[3],
        updated_at=row[4],
    )


def main() -> int:
    try:
        TursoDatabase(load_settings()).check_connection()
        print("Conexión Turso verificada con SELECT 1; no se modificaron datos.")
        return 0
    except ConfigurationError as error:
        print(str(error))
        return 1
    except ApiError:
        print("No se pudo conectar a Turso. Revisar URL, token y red.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
