"""Composición de la API: configuración, middlewares, errores y rutas.

Ejecutar desde backend/:

    uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
"""

import logging
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Final

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from upstash_blob import AsyncBucket

from app.agent_tokens import AgentTokenRepository, router as tokens_router
from app.api import router as users_router
from app.auth import SessionAuthenticator
from app.database import SqlUserRepository, TursoDatabase
from app.document_routes import router as documents_router
from app.documents import DocumentStore
from app.storage_preferences import StoragePreferences
from app.errors import register_error_handlers
from app.health import router as health_router
from app.request_context import REQUEST_ID_HEADER, track_request
from app.settings import Feature, Settings, load_settings

# Prefijo de las rutas de producto (API 02 en adelante). /health queda fuera
# porque comprueba el proceso, no forma parte del contrato versionado.
API_V1_PREFIX: Final = "/api/v1"

# Operaciones de perfiles, documentos y revocación de tokens personales.
CORS_METHODS: Final = ["GET", "PUT", "POST", "DELETE"]
CORS_HEADERS: Final = ["Authorization", "Content-Type"]

logger = logging.getLogger("copilot.api")


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = load_settings()

    app = FastAPI(title="Copilot API", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.authenticator = SessionAuthenticator(settings)
    app.state.users = None
    app.state.agent_tokens = None
    app.state.documents = None

    register_error_handlers(app)
    add_request_tracking(app)
    allow_frontend_origins(app, settings)
    app.include_router(health_router)
    app.include_router(users_router, prefix=API_V1_PREFIX)
    app.include_router(tokens_router, prefix=API_V1_PREFIX)
    app.include_router(documents_router, prefix=API_V1_PREFIX)
    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = app.state.settings
    preferences = None
    if not settings.missing_for(Feature.USERS):
        database = TursoDatabase(settings)
        preferences = StoragePreferences(database.connect)
        app.state.users = SqlUserRepository(database.connect)
        app.state.agent_tokens = AgentTokenRepository(database.connect)
    # Cada operación SQL abre y cierra su conexión; no se ejecuta DDL al arrancar.
    async with AsyncExitStack() as clients:
        if settings.upstash_blob_token:
            bucket = await clients.enter_async_context(AsyncBucket(
                settings.upstash_blob_token.get_secret_value(), enable_telemetry=False))
            app.state.documents = DocumentStore(bucket, settings.storage_namespace, settings.max_document_bytes, preferences)
        logger.info("API iniciada en entorno %s", settings.environment)
        try:
            yield
        finally:
            app.state.users = None
            app.state.agent_tokens = None
            app.state.documents = None
            logger.info("API detenida")


def add_request_tracking(app: FastAPI) -> None:
    app.add_middleware(BaseHTTPMiddleware, dispatch=track_request)


def allow_frontend_origins(app: FastAPI, settings: Settings) -> None:
    # Se añade después del seguimiento de peticiones para quedar por fuera:
    # así también las respuestas de error 500 llevan las cabeceras CORS.
    # CORS solo decide qué navegador puede leer la respuesta; no autentica.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
        expose_headers=[REQUEST_ID_HEADER],
        # El frontend envía el token en Authorization, no en cookies.
        allow_credentials=False,
    )


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


configure_logging()
app = create_app()
