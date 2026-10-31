# 01 — Copilot: API primero, frontend después

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Planificación vigente; preparación parcial implementada
Relacionada con: [registro del cambio](../bitacora-construccion/03-base-web-y-orden-api-frontend.md)

La aplicación será web: Nuxt 4 + Vue 3 + TypeScript con pnpm, y una API Python con FastAPI y uv. Clerk gestiona identidad, Turso guarda usuarios y Upstash Blob privado guarda documentos. El backend preparará Markdown y sintetizará audio; el navegador lo reproducirá. Esta es la decisión vigente del usuario.

## Orden para trabajar

| Paso | Plan | Se puede cerrar cuando… |
| --- | --- | --- |
| 1 | [API: arranque y configuración](plans/01-api-base-y-configuracion.md) | Arranca, valida env y responde salud sin secretos. |
| 2 | [API: Clerk y usuarios Turso](plans/02-api-identidad-y-usuarios.md) | JWT verificado y GET/PUT del perfil probados con Turso. |
| 3 | [API: documentos y Markdown](plans/03-api-documentos-blob-y-markdown.md) | Guardar, recuperar, preparar y aislar documentos funciona. |
| 4 | [API: voz y MCP](plans/04-api-voz-y-mcp.md) | Audio español evaluado, entrega autorizada y herramientas MCP verificadas. |
| 5 | [Frontend: acceso y panel](plans/05-frontend-acceso-y-panel-voz.md) | Nuxt conecta con la API terminada y permite leer/pausar/reiniciar. |

Ejecutar cada plan en este orden. Las comprobaciones de aceptación son trabajo previsto, salvo las registradas como ejecutadas en la bitácora. Preparar el frontend existente no adelanta la implementación del panel.

## Estado real

- `frontend/`: copia de estadistica-forms-web, renombrada copilot-web y adaptada de Descope a Clerk. Conserva organización y pantallas de acceso/cuenta. El panel Voz con estilo Focus todavía no existe.
- `backend/`: entorno uv y dependencias FastAPI, uvicorn, pydantic-settings y upstash-blob. Todavía no hay aplicación ASGI, rutas, conexión Turso, verificación JWT, parser ni motor de voz.
- `docs/` y `bitacora-construccion/`: documentación compartida en la raíz. La skill [construir-con-evidencia](../.agents/skills/construir-con-evidencia/SKILL.md) está en la raíz del proyecto, dentro de `.agents/skills`.
- Plugins Upstash y Turso instalados y habilitados para este proyecto; autenticación OAuth y recursos remotos pendientes.

## Contratos y fuentes

Leer [alcance](product/01-proposito-y-alcance.md), [recorrido](product/02-requisitos-y-recorrido.md), [arquitectura legible](product/03-arquitectura-y-legibilidad.md) y [datos y formatos](product/04-datos-y-formatos.md). Los [tres diagramas](diagrams/01-contexto-y-responsabilidades.md) describen el objetivo.

Fuentes: [filosofía y VOZ](fonts/04-contrato-voz-y-filosofia.md), [Focus](fonts/06-estilo-visual-focus-macos.md), [Markdown](fonts/08-markdown-pantalla-y-voz.md), [Blob](fonts/09-upstash-blob-y-herramientas.md), [Clerk](fonts/10-clerk-nuxt-y-python.md), [base Nuxt y cursos](fonts/11-base-nuxt-y-cursos.md), [Turso](fonts/12-turso-usuarios-python.md), [antecedentes recuperados](fonts/13-antecedentes-api-recuperados.md), [voz y MCP](fonts/14-voz-python-y-mcp.md).

No se crearon commits ni tags. El historial Git y el índice previo se conservan; los planes antiguos se sustituyen por petición expresa del usuario.
