# 06 — Revisión legible del frontend

Fecha de creación: 2026-10-31
Estado: Plan
Ámbito: frontend Nuxt (`frontend/app`)
Relacionada con: [plan backend 07](../07-reorganizar-backend-legible.md), [bitácora frontend 02](../../../bitacora-construccion/frontend/02-conexion-api-perfil-mcp-y-voz-en-vivo.md)
Revisión de referencia: `61cd4af` (tag `v0.3.0`)

## Objetivo

Revisar el frontend con las reglas de código legible y aplicar solo los ajustes que no cambian nada visible ni ninguna llamada a la API. La estructura ya está separada por responsabilidad (páginas, componentes, composables, servicios, tipos), así que no se mueven archivos.

## Hallazgos y ajustes

| Archivo | Hallazgo | Ajuste |
| --- | --- | --- |
| `services/api-client.ts`, `services/documents.ts` | La unión `'GET' \| 'POST' \| 'PUT' \| 'DELETE'` está repetida | Un tipo `HttpMethod` exportado |
| `services/documents.ts` | Cadena de `if` que traduce estado HTTP → tipo de fallo | Tabla con nombre `FAILURE_KIND_BY_STATUS` |
| `components/AccountStorage.vue` | Límites 1 y 100 escritos a mano, asignación encadenada `a = b = c` | Constantes con nombre, `isValidRetention()` y dos asignaciones |
| `components/AccountStorage.vue` | Junta credenciales MCP y retención (322 líneas) | Se propone separar en dos componentes; queda fuera porque movería mensajes de error en pantalla |

## Comprobación prevista

`pnpm typecheck`, `pnpm lint`, `pnpm format:check` y `pnpm build`. Además, comprobar en vista previa que Inicio, Voz y documento se ven igual.
