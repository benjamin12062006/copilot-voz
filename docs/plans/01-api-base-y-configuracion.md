# 01 — API: arranque y configuración

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [arquitectura](../product/03-arquitectura-y-legibilidad.md), [entorno preparado](../../backend/01-preparacion.md)

## Objetivo y punto de partida

Construir primero una API ejecutable independiente de Nuxt. Hoy `backend/` tiene un entorno uv reproducible; no tiene `app/main.py`. No implementar pantallas durante esta fase.

## Incrementos

1. Crear `app/main.py` con factoría/composición FastAPI y `GET /health` que responda `{ "status": "ok" }`. Separar liveness de comprobaciones remotas; no devolver env ni credenciales.
2. Crear Settings con pydantic-settings: entornos, CORS, Clerk, Turso, Blob, límites y acceso personal. Cargar explícitamente `.env` del backend al ejecutar localmente. Configuración requerida para cada funcionalidad debe fallar con nombres de variables, sin mostrar valores.
3. Definir contrato de errores y prefijo `/api/v1`. Diferenciar entrada inválida, sesión inválida y proveedor caído. Añadir request ID; logs sin contenido privado, Bearer ni secretos.
4. Preparar dependencias en lifespan y su cierre. Mantener una instancia por proceso cuando proceda. No conectar remotamente durante imports ni ejecutar migraciones destructivas al arrancar.
5. Configurar CORS para los orígenes concretos de Nuxt (`http://localhost:3000` y, si se usa, `http://127.0.0.1:3000`), métodos y Authorization. CORS no sustituye autenticación.

## Dependencias

Ya instaladas: FastAPI, uvicorn, pydantic-settings, upstash-blob. Clerk SDK, driver Turso, parser, MCP y voz se añaden en su paso, actualizando `uv.lock`. No instalar modelos grandes anticipadamente. El Python actual es 3.14; comprobar wheels de cada proveedor. Si voz necesita 3.12/3.13, cambiar requisito/versión y regenerar entorno como decisión documentada, sin romper el entorno global.

## Cierre previsto

`uv sync --locked`; ejecutar la API con `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` cuando exista el módulo. Verificar salud 200, configuración incompleta controlada, 404 de ruta inexistente, preflight permitido/rechazado y ausencia de secretos en respuestas/logs. No llamar a `/health` prueba de conexión Turso/Blob.

Salida: un comando reproducible, configuración descrita y servidor base comprobado. Continuar con [API 02](02-api-identidad-y-usuarios.md).
