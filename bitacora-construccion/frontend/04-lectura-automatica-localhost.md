# 04 — Lectura automática de documentos nuevos (prueba en localhost)

Fecha de creación: 2026-10-31
Última actualización: 2026-10-31
Estado: Implementado y verificado
Ámbito: frontend Nuxt
Relacionada con: [plan 07](../../docs/plans/frontend/07-lectura-automatica.md), [voz en vivo](02-conexion-api-perfil-mcp-y-voz-en-vivo.md), [despliegue](03-despliegue-vercel-y-cors.md)
Revisión de partida: `52a1059` (tag `v0.4.0`, solo local)

## Solicitud

La idea original de VOZ era escuchar cada redacción nueva en cuanto llega. El usuario preguntó si la web podía hacerlo sola, también con la pestaña en segundo plano, con una opción para elegir cuándo. Pidió probarlo primero en localhost, sin tocar lo desplegado, y guardar antes el estado con Git.

## Qué se hizo

- **Punto de guardado.** Tag anotado `v0.4.0` sobre `52a1059` (primer despliegue en producción), solo local. Las Actions publican al hacer push a `main` con cambios en `frontend/**` o `backend/**`; no se hizo push.
- **`composables/useAutoRead.ts`.**
  - `useAutoReadMode` guarda el modo (`off`, `agent`, `all`) en `localStorage`.
  - `useAutoReader`, arrancado una vez en `layouts/workspace.vue`, refresca la biblioteca cada 20 s con la opción encendida.
  - La primera lista hace de base. Los ids nuevos que cumplen el modo entran en una cola por orden de llegada y se leen con la voz en vivo existente cuando está libre.
  - Un candado Web Locks deja leer a una sola pestaña. Si el navegador aún no ha recibido un clic, la cola espera y se avisa una vez.
- **Perfil.** `AutoReadSettings.vue` añade el selector «Lectura automática».
- **Control desde cualquier vista.**
  - `WorkspacePage` muestra por defecto la barra de voz cuando hay una lectura.
  - `LiveVoiceBar` acepta `shows-document` (título enlazado y «Detener»).
  - En `voice/[id].vue`, abrir el documento que ya suena o salir de otro documento ya no corta esa lectura. Las lecturas manuales se comportan igual que antes.

Decisión pospuesta: guardar el modo en Turso (migración 004 y endpoint), hasta comprobar que la lectura en segundo plano funciona en el navegador del usuario.

## Comprobaciones

- `pnpm typecheck`, `pnpm lint` y `pnpm build` correctos.
- Prettier, sobre los archivos cambiados, correcto. El `format:check` global falla solo por `.vercel/output`, generado por el despliegue y ajeno a este cambio.
- En el navegador integrado, `localhost:3000` carga sin errores de consola hasta el acceso de Clerk. No se inició sesión por el usuario.

**Verificación del usuario:** activó el modo en Perfil, cambió de pestaña, envió un `.md` por el MCP y confirmó que se leyó solo. La opción pasó después a Turso: ver [backend 11](../backend/11-preferencias-de-voz-en-turso.md).
