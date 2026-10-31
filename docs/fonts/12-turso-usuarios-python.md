# 12 — Turso para usuarios desde Python

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Investigación; conexión pendiente
Relacionada con: [API usuarios](../plans/02-api-identidad-y-usuarios.md), [historial recuperado](13-antecedentes-api-recuperados.md)

Tipo de fuente: documentación oficial y antecedentes de código propio. Consulta: 2026-10-30.

F1 — [Python Quickstart](https://docs.turso.tech/sdk/python/quickstart), secciones remote/serverless y libSQL. La documentación diferencia el motor Turso del servicio libSQL: el driver debe corresponder al motor y URL de la base.

| Caso remoto | Paquete a evaluar en API 02 | URL esperada |
| --- | --- | --- |
| Motor Turso remoto | `turso_serverless` | `turso://…` |
| Base libSQL | `libsql` | `libsql://…` |

F2 — [Python reference](https://docs.turso.tech/sdk/python/reference): confirmar parámetros y API DB-API del paquete elegido. `pyturso` se orienta a uso local/embebido; no escogerlo por nombre para una base remota sin verificar.

La base aún no se ha elegido/conectado. No instalar ambos drivers ni inventar un endpoint. Variables de servidor: `TURSO_DATABASE_URL` y `TURSO_AUTH_TOKEN`.

F3 — [SQL de usuarios recuperado](13-antecedentes-api-recuperados.md): identidad separada del proveedor y restricción única issuer/subject. Adaptación propia a repositorio Python, SQL parametrizado y migraciones versionadas; sin Prisma ni sintaxis PostgreSQL.

## Plugin de desarrollo

Marketplace `tursodatabase/turso-mcp`, plugin `turso@turso` 0.1.0 instalado. Activado en `.codex/config.toml` de este proyecto; entrada global nueva desactivada. Endpoint de proveedor: `https://mcp.turso.ai/mcp`. OAuth no completado y ninguna base creada/consultada. Este MCP de proveedor es distinto del MCP de voz de nuestra app.
