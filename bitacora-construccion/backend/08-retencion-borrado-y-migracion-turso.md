# 08 — Preferencias de retención, borrado web y migración en Turso

Fecha de creación: 2026-10-31
Estado: Implementado y verificado
Ámbito: backend FastAPI y Turso
Relacionada con: [plan 06](../../docs/plans/06-conectar-api-perfil-y-eliminacion.md), [tokens personales](07-tokens-personales-y-textos-por-usuario.md), [fuentes MCP y Blob](../../docs/fonts/19-credenciales-mcp-personales.md)
Revisión de partida: `663e454` más incrementos locales 05–07, sin commit.

## Necesidad y punto de partida

El usuario pidió aplicar las migraciones en Turso, permitir configurar el límite automático de retención por usuario desde la web (20 por defecto, entre 1 y 100), añadir eliminación manual de documentos solo desde la web con comprobación de revisión y conectar el frontend en el puerto `3000` con FastAPI en `127.0.0.1:8000`.

Durante la prueba inicial en navegador, la pantalla `/session` mostró «Vamos a intentarlo de nuevo / No pudimos conectar con tu cuenta» porque el preflight CORS a `http://127.0.0.1:8000/api/v1/users/me` desde `http://localhost:3000` era rechazado: `backend/.env` tenía `COPILOT_CORS_ORIGINS` en el puerto `3070` y, tras actualizar `.env` al puerto `3000`, el proceso `uvicorn` previo seguía ejecutándose en segundo plano sin recargar las variables de entorno.

## Evidencia e interpretación

La escritura condicional del índice de biblioteca con ETag y la cola `pendingDeletes` garantizan que las versiones o documentos retirados por reducción de límite o borrado manual se eliminen del bucket sin reutilizar identificadores de archivo.[^F1] La autoridad del límite por propietario reside en Turso (`app_storage_preferences`) con clave foránea a `app_users(id) ON DELETE CASCADE`.[^F2]

## Alternativas y decisión

| Enfoque y fuente                                                                                            | Supuestos y ventajas para esta necesidad                                                                                                                                            | Coste o límite                                                | Decisión y motivo                                                                                                     |
| ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Guardar el límite en Turso y sincronizarlo en la biblioteca Blob al guardar o cambiar preferencia[^F1][^F2] | Mantiene el límite aunque la biblioteca Blob aún no exista; al reducir el límite retira inmediatamente los documentos antiguos sobrantes y encola sus archivos en `pendingDeletes`. | Requiere la migración `003_storage_preferences.sql` en Turso. | Elegido: la API aplica el mismo límite tanto a creaciones web como a envíos del agente MCP (`voice_submit_document`). |
| Exponer borrado o cambio de límite en MCP                                                                   | Permitiría administrar la biblioteca desde el chat.                                                                                                                                 | Contraviene la restricción expresa del usuario.               | Descartado: `mcp_server.py` expone únicamente `voice_submit_document`.                                                |

## Implementación y funcionamiento

| Decisión respaldada                                                    | Archivo y símbolo                                                                                                                                                                                                                                              | Adaptación realizada                                                                                                                                                                      |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Tabla y repositorio de límite por propietario (1..100, 20 por defecto) | [003_storage_preferences.sql](../../backend/migrations/003_storage_preferences.sql), [storage_preferences.py](../../backend/app/storage_preferences.py) (`StoragePreferences`), [migrations.py](../../backend/app/migrations.py) (`verify_preferences_schema`) | Persistencia en Turso e inspección de esquema para las migraciones 001–003.                                                                                                               |
| Rutas web de preferencias y borrado con revisión                       | [document_routes.py](../../backend/app/document_routes.py) (`storage_preferences`, `update_storage_preferences`, `delete_document`), [documents.py](../../backend/app/documents.py) (`DocumentStore.preferences`, `set_retention`, `delete`)                   | `PUT /api/v1/storage/preferences` recorta los documentos más antiguos si el límite baja; `DELETE /api/v1/documents/{id}?revision=…` exige revisión coincidente y propietario autenticado. |
| Conexión CORS y emisor Clerk con el frontend en `localhost:3000`       | [main.py](../../backend/app/main.py) (`CORS_METHODS`, `lifespan`), [settings.py](../../backend/app/settings.py)                                                                                                                                                | `CORS_METHODS` incluye `DELETE`; reinicio del proceso `uvicorn` tras actualizar `COPILOT_CORS_ORIGINS` a `http://localhost:3000` y `http://127.0.0.1:3000`.                               |
| Registro del servidor MCP en el proyecto para Zed y recarga de `.env`  | [.zed/settings.json](../../.zed/settings.json), [mcp_server.py](../../backend/app/mcp_server.py) (`voice_submit_document`)                                                                                                                                     | Apunta a `backend/mcp-clients/.env` mediante `COPILOT_MCP_ENV_FILE` sin guardar secretos en el JSON; recarga el archivo en cada envío por si el usuario rota su token.                    |

## Comprobación

| Comando, petición o prueba ejecutada                                                                                                                                                     | Resultado observado                                                                                                                                                                         |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `uv run --locked python -m app.migrations`                                                                                                                                               | `Esquema y migraciones verificados.` (migraciones 001, 002 y 003 verificadas en Turso).                                                                                                     |
| `uv run --locked python -m unittest discover -s tests -q`                                                                                                                                | 29 pruebas correctas, incluyendo borrado por propietario/revisión, persistencia de retención en Turso aplicada al agente y verificación de única herramienta MCP (`voice_submit_document`). |
| `curl -i -X OPTIONS http://127.0.0.1:8000/api/v1/users/me -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: authorization"` | `HTTP/1.1 200 OK` con `access-control-allow-origin: http://localhost:3000` y métodos `GET, PUT, POST, DELETE`.                                                                              |
| Invocación real de `voice_submit_document` desde el MCP de Zed                                                                                                                           | `{"documentId": "ce8d6f64-0bc0-5523-9980-cf8c43f582aa", "revision": 1}` guardado en Upstash Blob bajo el propietario autenticado.                                                           |

## Consecuencias y continuidad

El backend verifica tokens de Clerk contra el JWKS de la instancia configurada, persiste usuarios, tokens MCP y límites de retención en Turso, y guarda o elimina documentos en Upstash Blob. Si se cambia `.env` mientras `uvicorn` corre sin `--reload`, es necesario reiniciar el proceso para que las nuevas variables entren en vigor.

## Fuentes

[^F1]: [Credenciales MCP personales y escrituras condicionales Blob](../../docs/fonts/19-credenciales-mcp-personales.md). Consulta: 2026-10-31.

[^F2]: [Turso y usuarios en Python](../../docs/fonts/12-turso-usuarios-python.md). Consulta: 2026-10-31.
