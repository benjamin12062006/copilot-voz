"""Composición de la API: configuración, middlewares, errores y rutas.

Ejecutar desde backend/:

    uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Final

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.errors import register_error_handlers
from app.health import router as health_router
from app.request_context import REQUEST_ID_HEADER, track_request
from app.settings import Settings, load_settings

# Prefijo de las rutas de producto (API 02 en adelante). /health queda fuera
# porque comprueba el proceso, no forma parte del contrato versionado.
API_V1_PREFIX: Final = "/api/v1"

# Métodos que usa hoy el frontend (perfil GET/PUT). Cada plan añade los suyos.
CORS_METHODS: Final = ["GET", "PUT"]
CORS_HEADERS: Final = ["Authorization", "Content-Type"]

logger = logging.getLogger("copilot.api")


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = load_settings()

    app = FastAPI(title="Copilot API", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings

    register_error_handlers(app)
    add_request_tracking(app)
    allow_frontend_origins(app, settings)
    app.include_router(health_router)
    return app


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Aquí se abrirán y cerrarán los clientes de Turso, Blob y Clerk (API 02–03),
    # una instancia por proceso. Nada conecta en remoto durante los imports.
    logger.info("API iniciada en entorno %s", app.state.settings.environment)
    yield
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
