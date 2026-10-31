# 01 — Entorno del backend FastAPI

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Entorno preparado; API 01 implementada
Relacionada con: [orden de trabajo](../docs/01-indice.md), [clientes MCP](../docs/fonts/15-conexion-mcp-codex-y-claude.md)

## Preparado

`pyproject.toml`, `uv.lock`, `.python-version` y entorno `.venv` aislado. Dependencias: FastAPI, uvicorn, pydantic-settings y upstash-blob. `uv sync --locked --offline` y los imports del entorno se ejecutaron correctamente después de separar esta carpeta del frontend.

## Pendiente de implementar

API 01 añadió `app/` con configuración, contrato de errores, request ID, CORS y `GET /health` ([bitácora 04](../bitacora-construccion/04-api-base-y-configuracion.md)). Aún no existen rutas de producto, conexión Turso, verificación Clerk, parser Markdown, motor de voz ni servidor MCP propio. Ejecutar los planes [01](../docs/plans/01-api-base-y-configuracion.md) a [04](../docs/plans/04-api-voz-y-mcp.md) antes de desarrollar el panel Nuxt.

## Configuración

`.env.example` describe los nombres previstos para cada etapa; los nombres COPILOT son nuestros y deberán cargarse/validarse al implementar Settings. `.env` real está ignorado; no se publican claves ni se confía en que uv cargue por sí solo el archivo. Completar valores solo localmente o en el entorno de despliegue.

Para API 02: aplicación Clerk, issuer, authorized parties, IDs personales permitidos y credenciales de la base Turso elegida. Para API 03: bucket privado Upstash y token. Para API 04: modelo/voz aprobados tras escuchar muestras y credencial limitada de agente, con hash en API y token original solo en archivo privado del adaptador.

## Comandos válidos hoy

Desde `backend/`: `uv sync --locked` y `uv run --locked python -c "import fastapi, pydantic_settings, upstash_blob"`. Arrancar la API: `uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log`. El módulo stdio de las plantillas MCP será válido cuando se implemente.

[MCP clientes](mcp-clients/codex.toml.example) contiene solo una plantilla. No se activa contra un módulo ausente. Las comprobaciones de conexión remota requieren configuración real; no se han creado ni modificado recursos remotos.
