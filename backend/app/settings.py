"""Carga y validación de la configuración del backend.

Cada funcionalidad declara qué variables necesita. La API arranca aunque falten
las de funcionalidades futuras; esas se exigen con `Settings.require` cuando su
módulo se prepara, y el error nombra las variables sin mostrar sus valores.
"""

from enum import StrEnum
from pathlib import Path
from typing import Final, Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, SettingsError

BACKEND_DIR: Final = Path(__file__).resolve().parents[1]

# uv no carga `.env` por sí solo; se lee de forma explícita desde backend/.
# Las variables reales del entorno tienen prioridad sobre el archivo.
LOCAL_ENV_FILE: Final = BACKEND_DIR / ".env"

LOCAL_FRONTEND_ORIGINS: Final = ["http://localhost:3000", "http://127.0.0.1:3000"]

DEFAULT_MAX_DOCUMENT_BYTES: Final = 1_048_576


class Feature(StrEnum):
    IDENTITY = "identidad Clerk"
    USERS = "usuarios en Turso"
    DOCUMENTS = "documentos en Upstash Blob"
    AGENTS = "acceso MCP de agentes"


# Nombres de campo de `Settings` que cada funcionalidad necesita con valor.
# API 02–04 pueden ajustar su lista al elegir el mecanismo concreto.
FEATURE_REQUIREMENTS: Final[dict[Feature, tuple[str, ...]]] = {
    Feature.IDENTITY: (
        "clerk_issuer",
    ),
    Feature.USERS: ("turso_database_url", "turso_auth_token"),
    Feature.DOCUMENTS: ("upstash_blob_token",),
    Feature.AGENTS: ("turso_database_url", "turso_auth_token"),
}


class ConfigurationError(RuntimeError):
    """Configuración ausente o inválida. El mensaje nunca incluye valores."""


class Settings(BaseSettings):
    # Una variable vacía en `.env` (`CLERK_SECRET_KEY=`) cuenta como no configurada.
    model_config = SettingsConfigDict(env_ignore_empty=True, extra="ignore")

    environment: Literal["development", "test", "production"] = Field(
        default="development", validation_alias="COPILOT_ENV"
    )
    cors_origins: list[str] = Field(
        default=LOCAL_FRONTEND_ORIGINS, validation_alias="COPILOT_CORS_ORIGINS"
    )

    clerk_secret_key: SecretStr | None = Field(default=None, validation_alias="CLERK_SECRET_KEY")
    clerk_jwt_key: SecretStr | None = Field(default=None, validation_alias="CLERK_JWT_KEY")
    clerk_issuer: str | None = Field(default=None, validation_alias="CLERK_ISSUER")
    clerk_authorized_parties: list[str] = Field(
        default=[], validation_alias="CLERK_AUTHORIZED_PARTIES"
    )
    allowed_clerk_user_ids: list[str] = Field(
        default=[], validation_alias="COPILOT_ALLOWED_CLERK_USER_IDS"
    )

    turso_database_url: str | None = Field(default=None, validation_alias="TURSO_DATABASE_URL")
    turso_auth_token: SecretStr | None = Field(default=None, validation_alias="TURSO_AUTH_TOKEN")

    upstash_blob_token: SecretStr | None = Field(default=None, validation_alias="UPSTASH_BLOB_TOKEN")
    storage_namespace: str = Field(default="copilot/dev", validation_alias="COPILOT_STORAGE_NAMESPACE")
    max_document_bytes: int = Field(
        default=DEFAULT_MAX_DOCUMENT_BYTES,
        gt=0,
        validation_alias="COPILOT_STORAGE_MAX_DOCUMENT_BYTES",
    )


    @field_validator("cors_origins", "clerk_authorized_parties")
    @classmethod
    def require_exact_origins(cls, origins: list[str]) -> list[str]:
        for origin in origins:
            if not is_exact_origin(origin):
                # Sin el valor: el mensaje puede acabar en logs de arranque.
                raise ValueError("cada origen debe ser esquema://host[:puerto], sin ruta ni comodín")
        return origins

    @field_validator("turso_database_url")
    @classmethod
    def require_remote_libsql(cls, value: str | None) -> str | None:
        if value is None:
            return None
        parts = urlsplit(value)
        is_remote_database = (
            parts.scheme == "libsql"
            and bool(parts.hostname)
            and not (parts.username or parts.password or parts.query or parts.fragment)
            and parts.path in ("", "/")
        )
        if not is_remote_database:
            raise ValueError("debe ser una URL libsql:// remota, sin credenciales ni parámetros")
        return value

    @field_validator("clerk_issuer")
    @classmethod
    def require_clerk_origin(cls, value: str | None) -> str | None:
        if value is not None and not (is_exact_origin(value) and value.startswith("https://")):
            raise ValueError("debe ser el origen HTTPS exacto de la instancia")
        return value

    def require(self, feature: Feature) -> None:
        missing = self.missing_for(feature)
        if missing:
            raise ConfigurationError(f"Falta configurar {feature}: {', '.join(missing)}")

    def missing_for(self, feature: Feature) -> list[str]:
        """Variables de entorno de la funcionalidad que no tienen valor."""
        missing = []
        for field_name in FEATURE_REQUIREMENTS[feature]:
            if not getattr(self, field_name):
                missing.append(environment_variable_of(field_name))
        return missing


def load_settings(env_file: Path | None = LOCAL_ENV_FILE) -> Settings:
    try:
        return Settings(_env_file=env_file)
    except ValidationError as error:
        # `from None`: el error original de Pydantic guarda los valores recibidos
        # y aparecería en el traceback de arranque.
        raise ConfigurationError(describe_invalid_variables(error)) from None
    except SettingsError as error:
        raise ConfigurationError(f"No se pudo leer la configuración: {error}") from None


def describe_invalid_variables(error: ValidationError) -> str:
    problems = []
    for detail in error.errors(include_input=False, include_url=False):
        variable = ".".join(str(part) for part in detail["loc"])
        problems.append(f"{variable} ({detail['msg']})")
    return "Configuración inválida: " + "; ".join(problems)


def environment_variable_of(field_name: str) -> str:
    return str(Settings.model_fields[field_name].validation_alias)


def is_exact_origin(value: str) -> bool:
    parts = urlsplit(value)
    has_only_scheme_and_host = not (parts.path or parts.query or parts.fragment)
    has_credentials = parts.username is not None or parts.password is not None
    return (
        parts.scheme in ("http", "https")
        and bool(parts.hostname)
        and has_only_scheme_and_host
        and not has_credentials
    )
