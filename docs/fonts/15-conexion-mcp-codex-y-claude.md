# 15 — Conectar nuestro MCP a Codex y Claude Code

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan de conexión; plantillas inactivas
Relacionada con: [API 04](../plans/04-api-voz-y-mcp.md), [diagrama](../diagrams/01-contexto-y-responsabilidades.md)

Tipo de fuente: documentación oficial de clientes y CLI local. Consulta: 2026-10-30.

F1 — [OpenAI: Model Context Protocol](https://developers.openai.com/codex/mcp), configuración stdio y por proyecto. Codex acepta command/args/env y configuración local en `.codex/config.toml` para proyectos de confianza. CLI local contrastada con `codex mcp add --help`; no se registró aún el servidor de voz.

F2 — [Claude Code: Connect via MCP](https://code.claude.com/docs/en/mcp), stdio y project scope. Configuración compartida en `.mcp.json`, objeto `mcpServers`; admite command/args/env. La CLI `claude` no está disponible en el PATH comprobado en esta sesión: la prueba real de ese cliente queda pendiente, sin instalarlo por esta preparación.

## Preparación y activación futura

Plantillas de este proyecto, todavía inactivas:

- [Codex TOML](../../backend/mcp-clients/codex.toml.example).
- [Claude Code JSON](../../backend/mcp-clients/claude-code.json.example).
- [Variables privadas del adaptador](../../backend/mcp-clients/.env.example).

Las plantillas apuntan al módulo propuesto `app.mcp.stdio`, que aún no existe. Al cerrar API 04: comprobar ruta de uv y backend, crear archivo privado de configuración del adaptador, arrancar FastAPI y verificar handshake. Después fusionar la tabla de Codex con su configuración existente sin sustituir plugins ni otros MCP; fusionar el objeto Claude con `.mcp.json` existente. Para usarlo desde otro proyecto, registrar allí el adaptador o elegir alcance de usuario expresamente al integrarlo.

Los comandos de clientes lanzan el mismo adaptador stdio. No poner secretos en las plantillas ni en argumentos del proceso. El adaptador debe cargar explícitamente `COPILOT_MCP_ENV_FILE`; esa variable es una propuesta de nuestra aplicación, no una opción propia del cliente. El archivo solo tendrá URL de API y token de agente; no acceso a credenciales de proveedores.

## Criterios de cierre

Ambos clientes deben listar `voice_submit_document`, `voice_get_status`, `voice_list_documents`. Enviar un documento de prueba, comprobarlo por API y verlo luego en Nuxt. Si se pide generar audio, verificar job y binario. No declarar que se reprodujo: reproducción, pausa, continuar e inicio viven exclusivamente en Nuxt.

El MCP sirve contenido al lector; no lee carpetas del sistema, no ejecuta comandos y no hereda permisos de los agentes para hacerlo. Esta ficha es configuración planificada, no una integración ya conectada.
