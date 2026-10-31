# 02 — Acceso con Clerk y perfil simulado

Fecha de creación: 2026-10-31
Estado: Implementado con datos simulados — [bitácora frontend 01](../../../bitacora-construccion/frontend/01-pantallas-focus-nuxt-ui-y-clerk.md)
Ámbito: frontend Nuxt, acceso
Relacionada con: [plan 05 incremento 1](../05-frontend-acceso-y-panel-voz.md), [quickstart Clerk](../../fonts/frontend/02-clerk-nuxt-quickstart.md), [API 02](../02-api-identidad-y-usuarios.md)

## Objetivo

Activar Clerk de verdad (entrar, sesión, salir) con la estética Focus, y que el resto del recorrido funcione antes de que exista API 02.

## Punto de partida

El controlador `createAccessController` y el servicio de perfil existen. El módulo Clerk no se activaba: la variable usaba el prefijo `NEXT_PUBLIC_` y además `.env.local` no se cargaba.

## Decisiones

- Corregir el nombre de la variable y arrancar dev, build y preview con `--dotenv .env.local`, sin leer ni copiar valores.
- `NUXT_PUBLIC_DATA_SOURCE=mock` (valor por defecto): el perfil se construye desde el usuario de Clerk con la misma forma `AppUser` que devolverá `GET /users/me`. Con `api` se usa el servicio HTTP ya existente.
- Vista previa sin Clerk solo en desarrollo (`NUXT_PUBLIC_PREVIEW_SESSION=true`). Sirve para revisar el diseño sin iniciar sesión. Queda eliminada del build de producción mediante `import.meta.dev`.
- Rutas: `/auth`, `/session`; con sesión lista, `/home`, `/voice`, `/voice/new`, `/voice/:id` y `/account`. El middleware solo navega; la autorización es de la API.

## Incrementos

1. Variables y scripts.
2. Servicios de perfil simulado y sesión de vista previa.
3. Pantallas de acceso y sesión con `SignIn` integrado y su apariencia ajustada.
4. Destino de ruta según el estado, cubriendo todas las rutas del espacio de trabajo.

## Comprobación prevista

El módulo Clerk se carga con la clave del usuario y el formulario de Clerk se renderiza. La vista previa entra al espacio de trabajo. El login real con una cuenta del usuario lo comprueba el propio usuario: el agente no introduce credenciales.
