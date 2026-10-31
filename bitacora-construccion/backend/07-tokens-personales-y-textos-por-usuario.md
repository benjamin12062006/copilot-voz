# 07 — Tokens MCP personales y archivos por usuario

Fecha de creación: 2026-10-31
Estado: Implementado y verificado localmente y en Blob; migración Turso remota pendiente
Ámbito: backend; frontend sin modificaciones
Relacionada con: [plan](../../docs/plans/02.1-tokens-mcp-por-usuario.md), [fuentes](../../docs/fonts/19-credenciales-mcp-personales.md), [biblioteca anterior](06-biblioteca-blob-y-envio-mcp.md)
Revisión de partida: 663e454 más incrementos locales 05/06, conservados sin commit.

## Flujo implementado

Sesión Clerk válida → usuario local en Turso → emitir token MCP personal → copiarlo al cliente MCP → API valida hash/caducidad/revocación en cada envío → resolver propietario desde Turso → guardar archivos privados de ese propietario.

No se copia el token de sesión Clerk al agente como credencial permanente. La credencial personal tiene 256 bits aleatorios, dura 30 días y solo permite documents:submit. Turso guarda ID, user_id, hash, nombre, creación, expiración y revocación. La consulta de validación hace JOIN con app_users: un usuario eliminado no puede seguir enviando con su token. El valor original solo se devuelve al emitir, con Cache-Control:no-store; listar no devuelve token ni hash.

## Contrato para el botón del frontend

Todas estas rutas requieren Authorization: Bearer con token de sesión Clerk:

| Petición | Respuesta |
| --- | --- |
| POST /api/v1/mcp/tokens con {"name":"Codex"} | 201 con id, name, token, createdAt, expiresAt, scope. La UI muestra/copia token una sola vez. |
| GET /api/v1/mcp/tokens | {items:[metadata sin token ni hash]} solo del usuario actual. |
| DELETE /api/v1/mcp/tokens/{id} | 204; revocación permanente de ese token propio. Otro propietario recibe 404. |

POST crea el perfil local si todavía falta, usando únicamente la identidad verificada. No acepta userId/ownerId en el body. No hay token global o propietario fijo del agente en variables de entorno.

El cliente MCP mantiene su configuración existente: COPILOT_API_BASE_URL y COPILOT_MCP_API_TOKEN, donde ahora se coloca la credencial emitida por la web. Solo ofrece voice_submit_document. Los tokens MCP no autorizan rutas web ni emisión de más tokens. El adaptador rechaza HTTP remoto y URLs con credenciales/query; no sigue redirecciones.

## Blob y retención

Ruta calculada por servidor: `<namespace>/textos/<userId>/<fileId>.md` o `.txt`. S3 crea el prefijo al escribir; no se necesita un comando de crear carpeta. userId viene del usuario local en Turso, nunca de un argumento MCP. fileId es UUID de versión: editar conserva el ID lógico del documento y genera un archivo nuevo para evitar que escritores simultáneos se pisen.

La biblioteca ETag conserva metadata, originales y referencias; se mantienen los originales en el JSON por compatibilidad con el formato previo. Las bibliotecas antiguas sin fileId siguen siendo legibles; al editar un documento se crea su archivo de versión. No se trasladaron silenciosamente documentos existentes ni se borraron prefijos ajenos.

Confirmar biblioteca registra las versiones retiradas en pendingDeletes. Después se borran solo esas rutas UUID y se limpia la lista con ETag. El siguiente guardado reintenta pendientes antes de aceptar datos nuevos. No se devuelve éxito si falla el borrado; ante reintento MCP se conserva idempotencia mientras el documento siga retenido. Un fallo o cierre incierto entre escribir el archivo y confirmar la biblioteca puede dejar un archivo sin referenciar: límite explícito, sin prometer atomicidad entre objetos. Los originales antiguos retirados desaparecen del JSON actual y sus archivos de versión se eliminan tras confirmar el índice.

## Archivos

- [agent_tokens.py](../../backend/app/agent_tokens.py): generar → persistir hash; validar formato → buscar usuario → comparar hash/fechas; listar/revocar por propietario. Rutas Clerk delgadas.
- [002_mcp_tokens.sql](../../backend/migrations/002_mcp_tokens.sql) y [migrations.py](../../backend/app/migrations.py): historial por versión/checksum; actualización 001→002 sin cambiar usuarios ni adoptar tablas ajenas.
- [document_routes.py](../../backend/app/document_routes.py): propietario del agente resuelto en dependencia desde Turso; el token global anterior se retiró.
- [documents.py](../../backend/app/documents.py): archivos por usuario y versión, ETag y limpieza pendiente recuperable.
- [mcp_server.py](../../backend/app/mcp_server.py): misma herramienta y argumentos; protección del transporte de la credencial.

## Verificación y límites

27 pruebas locales correctas; compileall, enlaces documentales nuevos y git diff --check correctos.

Pruebas locales: emisión, solo hash en BD, aislamiento de listas y revocación, secreto incorrecto, expiración, revocación repetida, usuario eliminado, token MCP rechazado como sesión web, body con propietario rechazado, HTTP sin Clerk rechazado, actualización de migraciones conservando usuario, nombres de archivos por usuario, versiones reemplazadas borradas, máximo 20 y recuperación tras fallo de limpieza. Se conservan las pruebas previas, adaptando el contrato sustituido de token global.

Blob remoto: namespace temporal nuevo, Markdown exacto en textos/userId/fileId.md, edición con archivo nuevo, borrado de versión anterior y aislamiento de otra biblioteca comprobados. Se eliminó únicamente el namespace de validación recién creado.

No se modificó frontend ni se aplicó SQL en la base remota anteriormente identificada como database-estadistica-forms. Para activar emisión real falta configurar una base Copilot autorizada, ejecutar `uv run --locked python -m app.migrations --apply` y disponer del issuer Clerk real. El nuevo botón y su conexión corresponden al frontend; el contrato backend está listo.
