# 04 — API base: configuración, errores, request ID y salud

Fecha de creación: 2026-10-30
Estado: Implementado y verificado
Ámbito: backend FastAPI
Relacionada con: [plan API 01](../docs/plans/01-api-base-y-configuracion.md), [fuentes FastAPI](../docs/fonts/16-fastapi-base-curso.md), [entrada anterior](03-base-web-y-orden-api-frontend.md)
Revisión de partida: `199f42d` (tag `v0.1.0`, punto de control creado antes de este incremento)

## Necesidad y punto de partida

El usuario pidió ejecutar el plan 01 aplicando la filosofía de código legible. `backend/` tenía entorno uv y dependencias, pero ningún módulo ASGI. El frontend espera la API en `http://127.0.0.1:8000/api/v1` y solo interpreta códigos HTTP (401, 403, 404, resto como red).

## Evidencia e interpretación

El curso «FastAPI Completo» respalda: `Settings` tipado con `.env`[^F1], `main.py` con CORS, prefijo `/api/v1` y `lifespan`[^F2], ID por petición en un middleware[^F3] y orígenes concretos fuera de desarrollo[^F4]. El curso usa `*` y `load_dotenv` como atajos de desarrollo; aquí se descartan porque el plan exige orígenes concretos y carga explícita. Ocultar valores en errores, contrato JSON de errores y orden de middlewares son propuesta propia, comprobada contra los paquetes instalados.

## Alternativas y decisión

| Enfoque | Ventaja | Coste o límite | Decisión |
| --- | --- | --- | --- |
| Todas las variables requeridas al arrancar (F1) | Fallo temprano | Impide arrancar API 01 sin claves de Clerk/Turso que aún no se usan | Descartado |
| Variables por funcionalidad, exigidas con `Settings.require` | Arranca hoy; cada módulo exige lo suyo con nombres de variables | La lista exacta de API 02–04 puede cambiar | Elegido |
| CORS `*` (F2, F4) | Sin fricción en desarrollo | El plan pide orígenes concretos | Descartado; `*` se rechaza al cargar |
| ID de petición aceptado del cliente | Correlación extremo a extremo | Texto arbitrario en logs; suplantación | Descartado; lo genera el servidor |
| `/health` dentro de `/api/v1` | Una sola base URL | El plan lo define en la raíz; es salud del proceso, no contrato | `/health` en la raíz; `API_V1_PREFIX` reservado para API 02 |

## Implementación y funcionamiento

Flujo de una petición (de fuera hacia dentro): CORS → `track_request` (asigna ID, captura errores no controlados, registra) → manejadores de errores → rutas.

| Decisión | Archivo y símbolo | Adaptación |
| --- | --- | --- |
| Configuración tipada con `.env` explícito[^F1] | [settings.py](../backend/app/settings.py) `Settings`, `load_settings` | `env_ignore_empty`; secretos como `SecretStr`; errores de Pydantic convertidos a `ConfigurationError` con `from None` para que el traceback no lleve valores. |
| Exigir configuración por funcionalidad | `Feature`, `FEATURE_REQUIREMENTS`, `Settings.require`/`missing_for` | Mensaje: «Falta configurar usuarios en Turso: TURSO_DATABASE_URL, TURSO_AUTH_TOKEN». |
| Orígenes exactos[^F4] | `is_exact_origin`, `require_exact_origins` | Aplica a `COPILOT_CORS_ORIGINS` y `CLERK_AUTHORIZED_PARTIES`. |
| Contrato de errores | [errors.py](../backend/app/errors.py) `ErrorCode`, `ApiError`, `error_response`, `register_error_handlers` | `{"error":{code,message,requestId,details?}}`. Distingue `invalid_request` (422), `invalid_session` (401), `forbidden` (403) y `provider_unavailable` (503). Los detalles de validación dan campo y tipo de fallo, nunca el valor. |
| Request ID y log[^F3] | [request_context.py](../backend/app/request_context.py) `track_request`, `respond_or_report_failure`, `log_request` | Cabecera `X-Request-ID` expuesta por CORS; log con método, ruta sin query, estado, ms e ID. Un error no controlado responde 500 con el contrato dentro de CORS. |
| Composición y ciclo de vida[^F2] | [main.py](../backend/app/main.py) `create_app`, `lifespan`, `allow_frontend_origins` | CORS se añade después del seguimiento para quedar por fuera. Métodos `GET, PUT`; cabeceras `Authorization, Content-Type`; sin cookies. `lifespan` solo registra arranque/parada: aún no hay clientes que abrir (llegan en API 02–03). |
| Salud del proceso | [health.py](../backend/app/health.py) `read_health` | `{"status":"ok"}`, sin consultar proveedores. |

Comando de ejecución, desde `backend/`:

```bash
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

`--no-access-log` evita la línea de acceso de uvicorn, que incluye la query string; el log propio la sustituye.

Legibilidad aplicada: `create_app` se lee como pasos con nombre; condiciones con nombre (`is_exact_origin`, `code_for_status`); un `try/except` por función (`load_settings`, `respond_or_report_failure`); constantes con nombre (`CORS_METHODS`, `FEATURE_REQUIREMENTS`, `LOCAL_ENV_FILE`); comentarios solo para el porqué (orden de middlewares, `from None`, ID generado en servidor). No se crearon routers vacíos ni capas para módulos futuros. Tamaño: 6 archivos, 425 líneas con docstrings y comentarios.

## Comprobación

| Comprobación ejecutada | Resultado |
| --- | --- |
| `uv sync --locked`, `compileall` | Correctos; sin dependencias nuevas, `uv.lock` sin cambios. |
| Cargar la app con el `.env` real | Entorno `development`, 2 orígenes. Falta Clerk, Turso y MCP (esperado); Blob configurado. `repr` de Settings oculta secretos. |
| Servidor real uvicorn: `GET /health` | 200 `{"status":"ok"}` con `x-request-id`. |
| `GET /api/v1/no-existe` | 404 `not_found` con `requestId`. |
| `POST /health` | 405 `method_not_allowed`, cabecera `allow: GET`. |
| Preflight desde `http://localhost:3000` con PUT + Authorization | 200 con `access-control-allow-origin` del origen. |
| Preflight desde origen ajeno / método DELETE | 400 «Disallowed CORS origin» / «Disallowed CORS method». |
| GET con origen permitido y Bearer de prueba | 200, `access-control-expose-headers: X-Request-ID`. |
| Log del servidor tras enviar Bearer y `?nota=…` | Sin token, sin query (0 coincidencias). Arranque y «API detenida» registrados por `lifespan`. |
| Script temporal con rutas de prueba (fuera del proyecto) | 500 `internal_error` con CORS e ID igual en cabecera y cuerpo, sin texto de la excepción; 503 `provider_unavailable`; 401 `invalid_session`; 422 con `body.edad`/`int_parsing` sin el valor enviado. |
| Configuración inválida: `COPILOT_ENV`, origen `*`, origen con ruta y credenciales, JSON roto, límite negativo | Cada caso detiene el arranque con `ConfigurationError` que nombra la variable; el valor no aparece y no hay `ValidationError` encadenado. |
| `Settings.require(Feature.USERS)` sin `.env` | «Falta configurar usuarios en Turso: TURSO_DATABASE_URL, TURSO_AUTH_TOKEN». |

No hay suite de tests automatizados en el backend (pytest no está instalado y no se pidió). El JSON roto nombra el campo Python (`cors_origins`) en lugar de la variable: límite conocido de `SettingsError`. Aviso al importar `TestClient`: Starlette depreca `httpx` en favor de `httpx2`; no afecta al servidor.

## Consecuencias y continuidad

La API arranca con un comando reproducible, valida su configuración y responde salud sin secretos. API 02 debe: montar sus routers con `API_V1_PREFIX`, llamar `settings.require(Feature.IDENTITY)` y `Feature.USERS` al preparar sus clientes en `lifespan`, lanzar `ApiError(ErrorCode.INVALID_SESSION | FORBIDDEN | PROVIDER_UNAVAILABLE)` y ajustar `FEATURE_REQUIREMENTS` si elige `CLERK_JWT_KEY`. Al añadir métodos HTTP, ampliar `CORS_METHODS`. Revisar la exposición de `/docs` antes de producción.

## Fuentes

[^F1]: «236. Archivo de configuración y variables de entorno». Curso: FastAPI Completo. Sección 16: SQLModel - Modelos y Schemas - Devinote. Ruta relativa a la biblioteca de transcripciones: `FastAPI/FastAPI Completo/Sección 16 SQLModel - Modelos y Schemas - Devinote/236. Archivo de configuración y variables de entorno.md`. Líneas 13–25. Consulta: 2026-10-30. Ficha: [16](../docs/fonts/16-fastapi-base-curso.md).
[^F2]: «271. Configurando main.py». Curso: FastAPI Completo. Sección 17: SQLModel - Servicios y rutas - Devinote. Ruta: `FastAPI/FastAPI Completo/Sección 17 SQLModel - Servicios y rutas - Devinote/271. Configurando main.py.md`. Líneas 17–31. Consulta: 2026-10-30.
[^F3]: «223. Middleware - Generando Request ID». Curso: FastAPI Completo. Sección 15: Middlewares. Ruta: `FastAPI/FastAPI Completo/Sección 15 Middlewares/223. Middleware - Generando Request ID.md`. Líneas 13–21. Consulta: 2026-10-30.
[^F4]: «226. Middleware - CORS». Curso: FastAPI Completo. Sección 15: Middlewares. Ruta: `FastAPI/FastAPI Completo/Sección 15 Middlewares/226. Middleware - CORS.md`. Líneas 29–39. Consulta: 2026-10-30.
