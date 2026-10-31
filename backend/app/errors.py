"""Contrato de errores de la API.

Todas las respuestas de error tienen la misma forma:

    {"error": {"code": "...", "message": "...", "requestId": "..."}}

`code` es estable y es lo que debe leer un cliente; `message` es para personas.
Ninguna respuesta incluye valores recibidos, tokens ni configuración.
"""

from enum import StrEnum
from typing import Final

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorCode(StrEnum):
    CONFLICT = "conflict"
    TOO_LARGE = "too_large"
    INVALID_REQUEST = "invalid_request"
    INVALID_SESSION = "invalid_session"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    INTERNAL_ERROR = "internal_error"


ERROR_STATUS: Final[dict[ErrorCode, int]] = {
    ErrorCode.CONFLICT: 409,
    ErrorCode.TOO_LARGE: 413,
    ErrorCode.INVALID_REQUEST: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ErrorCode.INVALID_SESSION: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
    ErrorCode.NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.METHOD_NOT_ALLOWED: status.HTTP_405_METHOD_NOT_ALLOWED,
    ErrorCode.PROVIDER_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    ErrorCode.INTERNAL_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
}

DEFAULT_MESSAGES: Final[dict[ErrorCode, str]] = {
    ErrorCode.CONFLICT: "El documento cambió. Recarga antes de guardar.",
    ErrorCode.TOO_LARGE: "El documento supera el tamaño permitido.",
    ErrorCode.INVALID_REQUEST: "La solicitud no es válida.",
    ErrorCode.INVALID_SESSION: "La sesión no es válida o ha caducado.",
    ErrorCode.FORBIDDEN: "No tienes permiso para esta operación.",
    ErrorCode.NOT_FOUND: "El recurso no existe.",
    ErrorCode.METHOD_NOT_ALLOWED: "Este método no está permitido en esta ruta.",
    ErrorCode.PROVIDER_UNAVAILABLE: "Un servicio externo no está disponible. Inténtalo más tarde.",
    ErrorCode.INTERNAL_ERROR: "Error interno del servidor.",
}


class ApiError(Exception):
    """Error que las rutas y servicios lanzan para responder con el contrato."""

    def __init__(self, code: ErrorCode, message: str | None = None) -> None:
        self.code = code
        self.message = message or DEFAULT_MESSAGES[code]
        super().__init__(self.message)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, handle_api_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)


def error_response(
    request: Request,
    code: ErrorCode,
    message: str | None = None,
    details: list[dict[str, str]] | None = None,
    headers: dict[str, str] | None = None,
    status_code: int | None = None,
) -> JSONResponse:
    error = {
        "code": code.value,
        "message": message or DEFAULT_MESSAGES[code],
        "requestId": getattr(request.state, "request_id", None),
    }
    if details:
        error["details"] = details
    return JSONResponse(
        {"error": error},
        status_code=status_code or ERROR_STATUS[code],
        headers=headers,
    )


async def handle_api_error(request: Request, error: ApiError) -> JSONResponse:
    return error_response(request, error.code, error.message)


async def handle_http_error(request: Request, error: StarletteHTTPException) -> JSONResponse:
    # Llegan aquí las rutas inexistentes y los métodos no admitidos del enrutador.
    # Se conservan el estado original y sus cabeceras porque 405 incluye `Allow`.
    return error_response(
        request,
        code_for_status(error.status_code),
        headers=error.headers,
        status_code=error.status_code,
    )


async def handle_validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
    return error_response(request, ErrorCode.INVALID_REQUEST, details=describe_invalid_fields(error))


def describe_invalid_fields(error: RequestValidationError) -> list[dict[str, str]]:
    """Qué campo falló y por qué, sin repetir el valor recibido."""
    fields = []
    for detail in error.errors():
        location = ".".join(str(part) for part in detail["loc"])
        fields.append({"field": location, "issue": detail["type"]})
    return fields


def code_for_status(status_code: int) -> ErrorCode:
    if status_code == status.HTTP_404_NOT_FOUND:
        return ErrorCode.NOT_FOUND
    if status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return ErrorCode.METHOD_NOT_ALLOWED
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return ErrorCode.INVALID_SESSION
    if status_code == status.HTTP_403_FORBIDDEN:
        return ErrorCode.FORBIDDEN
    if status_code < status.HTTP_500_INTERNAL_SERVER_ERROR:
        return ErrorCode.INVALID_REQUEST
    return ErrorCode.INTERNAL_ERROR
