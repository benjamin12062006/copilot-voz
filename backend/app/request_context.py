"""Identificador por petición, registro de cada solicitud y red de seguridad
para errores no controlados.

El ID lo genera siempre el servidor: un valor enviado por el cliente no se
acepta porque podría inyectar texto en los logs o hacerse pasar por otra petición.
"""

import logging
import time
from typing import Final
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint

from app.errors import ErrorCode, error_response

REQUEST_ID_HEADER: Final = "X-Request-ID"

logger = logging.getLogger("copilot.api")


async def track_request(request: Request, call_next: RequestResponseEndpoint) -> Response:
    request_id = uuid4().hex
    request.state.request_id = request_id
    started_at = time.perf_counter()

    response = await respond_or_report_failure(request, call_next)

    response.headers[REQUEST_ID_HEADER] = request_id
    log_request(request, response.status_code, started_at)
    return response


async def respond_or_report_failure(request: Request, call_next: RequestResponseEndpoint) -> Response:
    try:
        return await call_next(request)
    except Exception:
        # Responder aquí, y no en el manejador global de Starlette, mantiene la
        # respuesta dentro de CORS y con request ID para que el cliente pueda citarlo.
        logger.exception("Error no controlado request_id=%s", request.state.request_id)
        return error_response(request, ErrorCode.INTERNAL_ERROR)


def log_request(request: Request, status_code: int, started_at: float) -> None:
    # Solo la ruta: la query string y las cabeceras (Authorization) quedan fuera del log.
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s (%.0f ms) request_id=%s",
        request.method,
        request.url.path,
        status_code,
        elapsed_ms,
        request.state.request_id,
    )
