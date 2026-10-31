# 07 — Lectura automática de documentos nuevos

Fecha de creación: 2026-10-31
Estado: Plan
Ámbito: frontend Nuxt (`frontend/app`), prueba en localhost
Relacionada con: [voz en vivo](05-voz-en-vivo.md), [fuente voz del navegador](../../fonts/frontend/03-voz-en-vivo-navegador.md), [despliegue](../../../bitacora-construccion/frontend/03-despliegue-vercel-y-cors.md)
Revisión de partida: `52a1059` (tag `v0.4.0`)

## Objetivo

Cuando un agente envía un Markdown por el MCP, Copilot lo lee en voz alta sin que la persona lo abra, también con la pestaña en segundo plano. La persona elige en Perfil cuándo ocurre: apagado, solo documentos de agentes o todos los nuevos.

Primero se prueba **solo en el frontend y en localhost**, con la opción guardada en el navegador. Si funciona, la opción pasa a Turso en un plan aparte (tabla nueva `app_voice_preferences`, migración 004, `GET`/`PUT` de preferencias).

## Mecanismo

1. **Detectar.** Con la opción encendida, la biblioteca se refresca cada 20 s (hoy solo al volver a la ventana). La primera lista es la base: lo que ya existía no se lee. Un id que no estaba es un documento nuevo. Una revisión nueva de un documento existente no se lee.
2. **Cola.** Los nuevos que cumplen el modo entran por orden de llegada. Si la voz está ocupada (lectura manual o en pausa), esperan a que termine.
3. **Leer.** Se pide el documento, se prepara con `prepareReading` y se lee con la voz en vivo existente. La barra de lectura aparece en cualquier vista del espacio para poder pausar o detener.
4. **Una sola pestaña lee.** Con Web Locks, la primera pestaña abierta es la lectora; las demás esperan.

## Límites del navegador (lo que se prueba)

- Chrome y Safari solo hablan si hubo un clic en la página desde que se abrió (activación del usuario). Tras recargar, la cola espera al primer clic y se avisa.
- En segundo plano, Chrome espacia los temporizadores: a partir de unos 5 minutos oculta, la consulta puede ir a una por minuto.
- «Ahorro de memoria» de Chrome puede descartar la pestaña. Cerrar la pestaña detiene todo.
- Un `.tsx` llega como bloque de código, que la voz omite.

## Archivos

| Archivo | Cambio |
| --- | --- |
| `types/voice.ts` | Tipo `AutoReadMode` |
| `composables/useAutoRead.ts` | Opción guardada (`useAutoReadMode`) y lector (`useAutoReader`) |
| `layouts/workspace.vue` | Arranca el lector una vez |
| `components/AutoReadSettings.vue`, `pages/account.vue` | Selector de modo en Perfil |
| `components/WorkspacePage.vue` | Barra de voz por defecto en el pie |
| `pages/voice/[id].vue` | Abrir o salir de un documento ya no corta la lectura de otro |

## Comprobación prevista

`pnpm typecheck`, `pnpm lint`, `pnpm format:check`, `pnpm build`. Prueba manual de la persona en localhost: activar en Perfil, cambiar de pestaña, enviar un `.md` desde un agente y escuchar. No se hace `git push`: subir a `main` despliega a producción con GitHub Actions.
