# 11 — Base Nuxt reutilizada y cursos consultados

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Fuentes verificadas y base copiada
Relacionada con: [filosofía](04-contrato-voz-y-filosofia.md), [Clerk](10-clerk-nuxt-y-python.md)

Tipo de fuente: código propio, originales de cursos y reconstrucción derivada. Consulta: 2026-10-30.

## F1 — Código de partida elegido por el usuario

[estadistica-forms-web](/Users/benji/Documents/KSuT/estadistica-forms-web), main `60e3f5982623d653353af92fcbfd68941909e442`. Se copiaron app/public/manifests/configuración; no `.env`, Git, dependencias, cachés ni documentación por encima de la propia de Copilot. Paquete renombrado `copilot-web`; dependencias luego instaladas por pnpm. Estructura `app/pages`, `layouts`, `components`, `composables`, `services`, `types`, `plugins`, `middleware`, `utils` conservada.

Fuente documental de origen: [fuentes de la migración web](/Users/benji/Documents/KSuT/estadistica-forms-web/docs/fonts/01-flutter-cursos-y-documentacion.md). Es evidencia secundaria; los pasajes originales siguientes fueron consultados, no se atribuye su investigación histórica a Copilot.

## F2 / R1 — Layouts

Biblioteca: `/Users/benji/Documents/chrome-extencions/trancripciones`.

Original: `Nuxt/Nuxt Full Stack/Sección 3 Nuxt - Primeros pasos/29. Nuxt Layout - Plantillas.md`, líneas 13–31. Curso en metadatos: «Server API, Middleware, Layouts, Caché, NuxtUI, Tailwind, Script Setup, Auth, Sesiones, SSR, SSG, SPA, Despliegues y más». Instructor llamado Fernando en el original; apellido no verificado.

R1: mismo directorio, `29. Nuxt Layout - Plantillas - Reconstrucción guiada.md`, fases 1–2, NuxtLayout/slot. Es reconstrucción derivada preexistente, con etiquetas inferidas y CSS adjunto ausente; no una app de curso ejecutada aquí.

Principio: layout compartido inserta la página mediante slot; adaptación a `frontend/app/app.vue` y `layouts/default.vue`. El diseño Focus es propio, no mostrado en la clase.

## F3 — Acciones y middleware

Mismo curso, sección `Sección 7 Autenticación y autorización`:

- `85. useAuthentication - Composable personalizado.md`, líneas 17–25: estado/acciones en composable y `$fetch` para acciones. Aplicación: `useAccess` y `createProfileService`; no copiar login por contraseña del ejemplo.
- `88. Route Middlewares.md`, líneas 13–37: middleware de navegación, sufijo global y devolver redirección sin bucles. Aplicación: `access.global.ts`; FastAPI sigue siendo el límite de autorización.

## F4 — Componentes legibles

Original: `Vue/Vue 3 con TypeScript y Quasar/Sección 2 Vue.js + Composition API + TypeScript - Primeros Pasos/13. Consideraciones del Script Setup.md`, líneas 23–25. Instructor no identificado en el archivo. Curso en metadatos: «Vue 3, Pinia, Vite, TypeScript, Composition API, Script Setup, Vue-Query, Quasar, Caché y más».

Principio conceptual: extraer lógica que crece a composables. Interpretación propia: separar por responsabilidad, sin límite rígido de líneas ni archivos vacíos. No se reconstruye un contador para justificar esa separación.

## Documentación y estado

[Nuxt app structure](https://nuxt.com/docs/4.x/directory-structure/app), [Runtime Config](https://nuxt.com/docs/4.x/guide/going-further/runtime-config), [pnpm runtime](https://pnpm.io/package_json#devenginesruntime). Versiones efectivas: Nuxt 4.6.2, Vue 3.5.44, TypeScript 6.0.3, pnpm 12.5.1, Node de scripts 24.19.0; no actualizar sin necesidad. Clerk se fundamenta en la [ficha 10](10-clerk-nuxt-y-python.md), no en estos cursos.

La copia contiene acceso/cuenta; el lector y el rediseño están pendientes del [plan frontend](../plans/05-frontend-acceso-y-panel-voz.md).
