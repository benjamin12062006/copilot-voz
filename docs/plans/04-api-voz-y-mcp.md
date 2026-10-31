# 04 — API: síntesis de voz y conexión MCP

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [voz y MCP](../fonts/14-voz-python-y-mcp.md), [clientes](../fonts/15-conexion-mcp-codex-y-claude.md), [secuencia](../diagrams/02-guardar-y-reproducir.md)

## Objetivo

Generar audio desde documentos preparados y permitir que Codex o Claude Code envíen contenido al lector mediante un MCP propio. Depende de los contratos de identidad y documentos. La parte visual y todos los controles de reproducción pertenecen a Nuxt: el backend no pausa, continúa ni reinicia un reproductor.

## A — Síntesis, antes de integrar interfaz

1. Spike de Kokoro-ONNX en español: verificar compatibilidad Python/CPU, disponibilidad de modelo/voces y sus licencias; comparar muestras con Piper si hace falta. Medir inicio frío, memoria máxima, tiempo por longitud y pronunciación con textos del usuario. No se ha escuchado ni instalado un modelo todavía. [Fuentes](../fonts/14-voz-python-y-mcp.md).
2. Elegir motor tras las medidas. Aislar `SpeechGenerator` del proveedor y mantener el modelo en memoria por proceso. Limitar longitud, cola, concurrencia y caducidad; no bloquear el event loop ni cargar modelos por petición.
3. `POST /api/v1/speech/jobs` con `{documentId,revision,voiceId}` → 202 `{job:{id,status}}`. Comprobar propiedad y revisión; usar preparación de API 03. Capturar versión de preparación/motor/voz. Misma clave de idempotencia del usuario no crea trabajos duplicados.
4. `GET /api/v1/speech/jobs/{id}` → estado queued/running/ready/failed/expired y datos de artefacto cuando esté listo. `GET /api/v1/speech/jobs/{id}/audio` → binario con tipo correcto, solo autorizado. No devolver rutas locales ni poner Bearer en query.
5. Audio temporal con propietario y caducidad; limpiar artefactos propios. Definir fallos, cancelación de generación cuando sea posible y reinicio del servidor. No comunicar ready sin audio completo disponible.

Nuxt descargará el audio autorizado como Blob y creará un Object URL; así `HTMLAudioElement` no necesita enviar un Bearer en su atributo src. El usuario pulsa reproducir. `pause`, `play` y `currentTime = 0` se ejecutan únicamente en Nuxt. No existirán herramientas MCP pause/resume/restart en el alcance inicial.

## B — MCP propio compatible con agentes

1. Añadir SDK oficial Python MCP y fijar su versión comprobando su API estable. Crear un adaptador stdio que llame a nuestra API FastAPI; no duplicar documentos, parser ni motor.
2. Primer transporte: stdio local lanzado por Codex/Claude Code, con stdout reservado al protocolo y logs por stderr. FastAPI corre como servicio separado. La integración es propia, distinta de los plugins Turso/Upstash instalados para administrar proveedores.
3. El adaptador carga configuración privada desde un archivo dedicado, ignorado por Git, que contiene URL de API y token de servicio limitado a voz/documentos. No entregar a un proceso MCP las claves de Turso, Blob o Clerk.
4. La API acepta esta credencial solo en rutas de agente acotadas: identidad de propietario fija configurada en servidor, usuario local ya creado en API 02, scopes explícitos y token revocable. No aceptar ownerId de argumentos del agente. Propuesta: `COPILOT_MCP_TOKEN_SHA256` en backend; token aleatorio original solo en archivo privado del adaptador. No reutilizar un JWT de Clerk de otro recurso.
5. Publicar estas herramientas con schemas y resultados estructurados:

| Herramienta | Entrada | Resultado |
| --- | --- | --- |
| `voice_submit_document` | title, format, original, idempotencyKey, generateAudio opcional | documentId, revision y jobId si se solicitó síntesis. |
| `voice_get_status` | documentId o jobId propio | Estado de guardado/preparación/generación; nunca afirma que se está escuchando. |
| `voice_list_documents` | cursor opcional y límite | Resúmenes propios, paginados. |

`voice_submit_document` acepta Markdown y texto plano; es la entrada desde una respuesta de Codex/Claude Code a nuestra biblioteca. El texto de un documento es dato no confiable, no instrucciones que amplían permisos del MCP. Generar audio no lo reproduce en el Mac ni en el navegador.

6. El panel Nuxt obtiene documentos de la API y refresca biblioteca/estado al volver a la ventana y mediante consulta acotada mientras hay un trabajo activo. Al recibir contenido del agente puede mostrar «Nuevo documento»; la reproducción requiere interacción del usuario y respeta restricciones del navegador. SSE queda para una evolución si el polling es insuficiente.
7. Preparar y verificar configuración para ambos clientes según [conexión MCP](../fonts/15-conexion-mcp-codex-y-claude.md). Registrar servidor activo solo después de implementar el módulo y probar handshake/listado de herramientas. No anunciar conexión funcional con una plantilla vacía.

## C — Evolución remota

Si el MCP debe funcionar sin proceso local, añadir Streamable HTTP y autorización compatible con MCP (audience/resource y OAuth para clientes externos). Verificar integración de cada cliente. No publicar el token personal en una URL ni reenviar session tokens a recursos arbitrarios. Esta evolución no bloquea el primer MCP stdio personal.

## Cierre previsto

Audio español evaluado y disponible solo al propietario; errores de modelo/cola/archivo caducado; generación repetida idempotente. MCP: handshake, tools/list y llamada real desde Codex y desde Claude Code cuando esté instalado; enviar `.md` → documento visible por API → job ready → audio autorizado. Comprobar argumentos inválidos, token revocado y aislamiento. La pausa/reinicio se comprobarán en [Frontend 05](05-frontend-acceso-y-panel-voz.md), nunca como función del servidor.
