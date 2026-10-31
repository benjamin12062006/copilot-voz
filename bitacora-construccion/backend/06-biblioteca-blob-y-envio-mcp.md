# 06 — Biblioteca Blob y único envío MCP

Fecha de creación: 2026-10-31
Estado: Implementado y verificado; registro de clientes e integración frontend pendientes
Relacionada con: [plan 03](../../docs/plans/03-api-documentos-blob-y-markdown.md), [plan 04](../../docs/plans/04-api-voz-y-mcp.md), [fuentes](../../docs/fonts/18-blob-condicional-y-mcp-python.md), [antecedente](05-api-usuarios-turso.md)
Revisión de partida: 663e454 más cambios locales del incremento anterior, conservados sin commit.

## Alcance y decisiones

Se revisaron tipos y servicios simulados del frontend sin modificarlos. Se implementaron almacenamiento privado, crear/listar/leer/actualizar/preparar documentos y un solo envío MCP Markdown. El usuario autorizó retirar documentos al superar 20, sustituyendo el plan anterior que aplazaba toda retención.

Una biblioteca JSON por propietario contiene hasta 20 documentos, incluidos originales. Guardar y retirar el más antiguo ocurre en una sola escritura ETag; creación condicional y reintentos resuelven concurrencia entre procesos. El contenido retirado deja de estar en el objeto actual. No se promete borrar backups internos del proveedor. Cada guardado reescribe la biblioteca completa, aproximadamente hasta 20 MiB más metadata: coste aceptado para evitar índices, objetos huérfanos y bloqueos distribuidos en una biblioteca pequeña. Las ediciones cuentan como guardados recientes.

## Código y responsabilidades

- [documents.py](../../backend/app/documents.py): validate_content → cargar biblioteca → comprobar revisión/idempotencia → construir documento → retener 20 → confirmar ETag. Owner y namespace se calculan en servidor; no se acepta una ruta Blob del agente.
- [document_routes.py](../../backend/app/document_routes.py): entradas HTTP delgadas; propietario web desde identidad/perfil, propietario MCP fijo y hash de token comparado en tiempo constante. SQL síncrono se resuelve en dependencia de FastAPI fuera del event loop.
- [prepare_document.py](../../backend/app/prepare_document.py): parser CommonMark con tablas; bloques para el contrato existente, texto hablado y avisos de código omitido. No descarga recursos ni ejecuta HTML. Listas anidadas se aplanan al contrato de items de texto; no se promete GFM completo.
- [mcp_server.py](../../backend/app/mcp_server.py): única herramienta voice_submit_document, stdio con SDK oficial 2.3.0; llama a la API, sin secretos Blob/Turso. Responde guardado, no reproducción.
- [main.py](../../backend/app/main.py): AsyncBucket abre/cierra en lifespan, telemetría desactivada, CORS añade POST. No hay migraciones ni borrados durante imports/arranque.

Campos del frontend conservados: content, markdown/text, revision numérica, updatedAt, wordCount, origin y notices. GET documents devuelve items/nextCursor:null. POST/GET/PUT devuelven document; prepared recibe revision por query. Email/usuarios no se modificaron.

## Verificación

19 pruebas locales correctas; compileall y git diff --check sin errores.

Pruebas locales de retención 21→20 y retiro del contenido, aislamiento, persistencia exacta CRLF/acentos, conflictos, tamaño UTF-8, reintentos concurrentes y reinicio del servicio, preparación Markdown/texto y única herramienta. Recorrido herramienta→HTTP→biblioteca y autorización de agente comprobados con ASGI y bucket controlado. Se conservan las pruebas anteriores.

MCP real por subprocess stdio: initialize y tools/list correctos, solo voice_submit_document. Blob remoto con namespace de validación nuevo: crear, repetir, actualizar revision 2 y leer original exacto correctos. Solo ese objeto temporal se eliminó al terminar; no se tocaron documentos existentes.

## Límites y ejecución

La idempotencia dura mientras el documento esté retenido: reenviar una clave retirada por antigüedad puede crear de nuevo el documento. Un conflicto repetido agota seis intentos y devuelve 409; proveedor caído devuelve 503. Los agentes necesitan el token de servicio y el UUID local del mismo propietario usado por web, configurados mediante los campos ya previstos. No se generaron credenciales ni se registraron clientes sin configuración real.

Arrancar API con el comando habitual. MCP: uv run --locked python -m app.mcp_server. Las plantillas de mcp-clients apuntan al módulo implementado y cargan su .env privado (COPILOT_API_BASE_URL y COPILOT_MCP_API_TOKEN). No se generó audio ni se conectó frontend.
