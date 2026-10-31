# 02 — Clerk Nuxt: quickstart y componentes instalados

Fecha de creación: 2026-10-30
Tipo de fuente: documentación oficial y paquete instalado
Origen: Clerk Docs; `@clerk/nuxt` 3.1.19 instalado
Fecha de consulta: 2026-10-30
Relacionada con: [plan frontend 02](../../plans/frontend/02-acceso-clerk.md), [Clerk general](../10-clerk-nuxt-y-python.md)

## Necesidad de consulta

El usuario pidió integrar Clerk siguiendo el quickstart de Nuxt. El frontend ya tenía el adaptador, pero el módulo no se activaba.

## Localización verificable

| ID | Fuente | Sección |
| --- | --- | --- |
| K1 | [Nuxt Quickstart (manual)](https://clerk.com/docs/nuxt/getting-started/quickstart.md?manual=1) | Install, environment variables, `nuxt.config.ts`, `app.vue` |
| K2 | `node_modules/@clerk/nuxt/dist/runtime/components/index.js` | Lista de exports |
| K3 | `@nuxt/cli` 4.0.1 / `c12` 3.3.4 instalados | Carga de dotenv: `fileName: options.fileName ?? ".env"` |

## Evidencia

- **K1:** variables `NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY` y `NUXT_CLERK_SECRET_KEY` en `.env`; registrar `'@clerk/nuxt'` en `modules`, que configura middleware, plugins y componentes. Ejemplo con `<Show when="signed-in">`/`"signed-out"`, `SignInButton` y `UserButton`. La versión de la página dice que `SignedIn`/`SignedOut` son de Core 2.
- **K2:** el paquete instalado exporta `Show`, `SignIn`, `SignInButton`, `SignOutButton`, `UserButton`, `UserAvatar` y `UserProfile`.
- **K3:** Nuxt carga solo `.env` salvo que se indique otro archivo con `--dotenv`.

## Interpretación y límites

El `.env.local` existente usaba el prefijo `NEXT_PUBLIC_` de Next.js y además no se cargaba. Por ambas razones `nuxt.config.ts` nunca veía la clave y el módulo quedaba desactivado. No se leyeron ni se copiaron los valores de las claves. El quickstart no cubre estilos; el tema del componente `SignIn` (`appearance.variables`) es adaptación propia.

## Aplicación en el proyecto

- Renombrar la variable a `NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY` y arrancar con `--dotenv .env.local`.
- Mantener el controlador de acceso propio. `SignIn` embebido con apariencia Focus, y `UserAvatar` en el lateral.
- La sesión real sigue dependiendo de las claves del usuario; la API valida tokens en API 02.
