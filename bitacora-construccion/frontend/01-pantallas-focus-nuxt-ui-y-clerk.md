# 01 — Pantallas Focus con Nuxt UI, Clerk conectado y datos simulados

Fecha de creación: 2026-10-31
Estado: Implementado; verificado con sesión de vista previa y formulario real de Clerk. Login completo con cuenta real pendiente del usuario.
Ámbito: frontend Nuxt
Relacionada con: [plan 05](../../docs/plans/05-frontend-acceso-y-panel-voz.md), subplanes [01](../../docs/plans/frontend/01-tema-focus-y-espacio-de-trabajo.md) · [02](../../docs/plans/frontend/02-acceso-clerk.md) · [03](../../docs/plans/frontend/03-biblioteca-editor-y-datos-simulados.md) · [04](../../docs/plans/frontend/04-lector-y-reproductor.md), fuentes [Nuxt UI](../../docs/fonts/frontend/01-nuxt-ui-instalacion-y-tema.md) · [Clerk](../../docs/fonts/frontend/02-clerk-nuxt-quickstart.md) · [Focus](../../docs/fonts/06-estilo-visual-focus-macos.md)
Revisión de partida: `663e454` (tag `v0.2.0`)

## Necesidad y punto de partida

El usuario pidió construir ya las pantallas del plan 05, con el aspecto de la captura Focus, usando Nuxt UI y Tailwind. También pidió conectar Clerk según su quickstart de Nuxt y simular lo que todavía no da la API. El plan 05 exigía cerrar antes API 01–04; esa condición la cambió el usuario de forma expresa. Por eso el plan se dividió en cuatro subplanes en `docs/plans/frontend/`.

Al empezar, el módulo Clerk no se activaba por dos motivos. La clave usaba el prefijo de Next.js (`NEXT_PUBLIC_…`), y Nuxt solo carga `.env`, no `.env.local` ([ficha Clerk](../../docs/fonts/frontend/02-clerk-nuxt-quickstart.md), K3).

## Evidencia y decisiones

| Necesidad | Evidencia | Decisión |
| --- | --- | --- |
| Base de componentes | Nuxt UI 4.12: módulo, `@import "@nuxt/ui"`, `UApp`, variables `--ui-*` ([U1, U2](../../docs/fonts/frontend/01-nuxt-ui-instalacion-y-tema.md)) | Superficies ajustadas solo con variables CSS; componentes Dashboard, NavigationMenu, Tabs, FileUpload, Slider, Empty y Toast sin reescribirlos. |
| Aspecto Focus | Píxeles medidos en la captura: lateral `#4c4551`, principal `#362e38`, fila activa `#5f5661`, texto `#fbf7fb`, atenuado `#978d9b`, y nueve colores de cabecera | Tokens en `.dark`; variante clara propia. Cabecera `FocusCover` en SVG propio, sin copiar la imagen. Tipografía del sistema con título en peso 300. |
| Clerk | Quickstart: `NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `NUXT_CLERK_SECRET_KEY` y módulo `@clerk/nuxt` (K1). Variables de `appearance` vigentes (`colorForeground`, `colorInput`…) | Variable renombrada sin leer su valor; los scripts usan `--dotenv .env.local`. `SignIn` integrado con los colores Focus. |
| Datos sin API | Contratos de API 02–04 en los planes | Servicios simulados en `services/mock/`, con la misma forma que la API. El perfil sale del usuario de Clerk. Los documentos se guardan en `localStorage`. La voz es un WAV silencioso con la duración estimada. |
| Revisar sin login | — (propuesta propia) | `pnpm dev:preview`: sesión falsa solo con `import.meta.dev`; comprobado que no aparece en el build. |

## Implementación

| Pieza | Archivo y símbolo |
| --- | --- |
| Tema y tokens | [main.css](../../frontend/app/assets/css/main.css), [app.config.ts](../../frontend/app/app.config.ts), [nuxt.config.ts](../../frontend/nuxt.config.ts) (`ui.fonts: false`, oscuro por defecto, iconos Lucide locales) |
| Ventana de acceso | [layouts/default.vue](../../frontend/app/layouts/default.vue), [auth.vue](../../frontend/app/pages/auth.vue), [session.vue](../../frontend/app/pages/session.vue), [ClerkAccess.client.vue](../../frontend/app/components/ClerkAccess.client.vue) |
| Espacio de trabajo | [layouts/workspace.vue](../../frontend/app/layouts/workspace.vue): tarjetas «Todos/Agentes», secciones «Espacio» y «Formatos» y menú de cuenta. [WorkspacePage](../../frontend/app/components/WorkspacePage.vue) y [FocusCover](../../frontend/app/components/FocusCover.vue) |
| Sesión y perfil | [plugins/access.client.ts](../../frontend/app/plugins/access.client.ts) (`connectClerk`, `chooseProfiles`, `followAccessState`), [access-route.ts](../../frontend/app/utils/access-route.ts) (`accessRoute`, `isWorkspacePath`), [preview-session.ts](../../frontend/app/services/preview-session.ts) |
| Documentos | [types/documents.ts](../../frontend/app/types/documents.ts) (`DocumentService`), [mock/documents.ts](../../frontend/app/services/mock/documents.ts), [mock/prepare-markdown.ts](../../frontend/app/services/mock/prepare-markdown.ts), [useDocumentLibrary](../../frontend/app/composables/useDocumentLibrary.ts) |
| Pantallas | [home.vue](../../frontend/app/pages/home.vue), [voice/index.vue](../../frontend/app/pages/voice/index.vue), [voice/new.vue](../../frontend/app/pages/voice/new.vue), [voice/[id].vue](../../frontend/app/pages/voice/[id].vue), [account.vue](../../frontend/app/pages/account.vue) |
| Lectura y voz | [DocumentBlocks](../../frontend/app/components/DocumentBlocks.vue) (solo texto, nunca HTML), [DocumentEditor](../../frontend/app/components/DocumentEditor.vue) (importación UTF-8 estricta), [voice-player.ts](../../frontend/app/services/voice-player.ts) (`createVoicePlayer`: un solo audio, intentos que descartan respuestas tardías), [VoicePlayerBar](../../frontend/app/components/VoicePlayerBar.vue) |

Dependencias: `@nuxt/ui` 4.12.0, `marked` 18.1.1 (solo para el simulador) y `@iconify-json/lucide` 1.2.144, con versiones de al menos dos semanas. Se retiraron `@fontsource/roboto` y `@tailwindcss/vite`, porque Nuxt UI ya integra Tailwind. `vue-demi` queda sin script de instalación (`allowBuilds: false`).

## Comprobación

| Comprobación | Resultado |
| --- | --- |
| `pnpm typecheck`, `pnpm lint`, `pnpm format:check` | Sin errores. |
| `pnpm build` | Correcto. Ni la identidad de vista previa ni `sk_test_` aparecen en `.output`. |
| Variables de Clerk (validadas sin imprimir valores) | `pk_test_`/`sk_test_` del mismo entorno; la clave publicable decodifica a una instancia `clerk.accounts.dev`. |
| `pnpm dev` con Clerk real, sin sesión | `/auth` → «Continuar» → se ve el `SignIn` de Clerk con colores Focus. Consola: solo el aviso de claves de desarrollo. |
| Vista previa a 1280 px | Inicio, Voz, documento, nuevo y cuenta con lateral, cabecera y filas como la referencia. |
| Reproductor | Escuchar → 0:08 → pausa en 0:09 → Espacio continúa → volver al inicio 0:00 → fin «Lectura terminada». |
| Salir durante la generación | Al volver a Voz el reproductor queda `idle` y el audio tardío se descarta. |
| Crear y editar | Crear → aviso y contadores actualizados (6 en total, 4 en Markdown). Conflicto forzado con otra revisión → aviso, y el borrador conserva «(mi cambio)». «Descartar y recargar» carga la versión ajena. |
| Recargar `/voice` | Fallo encontrado: acababa en `/home`. Corregido en `accessRoute`, que ahora mantiene la ruta durante la carga; queda pendiente volver a comprobarlo en navegador. |

## Pendiente

- Login completo con tu cuenta. En el panel de Clerk la aplicación se llama «Notes» y solo está activado Google; se cambia allí, no en el código.
- Lateral en móvil: el botón abre el diálogo (está en el DOM con su contenido), pero no se vio en la captura. Falta investigarlo.
- El elemento activo del lateral usa violeta; en Focus es solo un fondo más claro.
- Al conectar API 02–04: `NUXT_PUBLIC_DATA_SOURCE=api` ya cambia el perfil. Para documentos y voz hay que crear servicios HTTP con los mismos contratos y borrar `services/mock/` (y `marked`).
