# 02 — Investigación y decisiones del despliegue

Fecha de creación: 2026-10-31
Estado: Investigación aplicada
Relacionada con: [procedimiento](01-procedimiento-fastapi-vercel.md), [errores](03-errores-y-soluciones.md), [fuentes previas](../../../docs/fonts/22-vercel-fastapi-y-github-actions.md)

## Comparación realizada

| Opción | Evidencia | Decisión aplicada |
| --- | --- | --- |
| Cloudflare Containers | Linux permite conservar el controlador nativo `libsql`; requiere Workers Paid | Se preparó inicialmente y se retiró cuando el usuario eligió Vercel |
| Python Workers | Usa Pyodide/WebAssembly y exige compatibilidad de paquetes; FastAPI está soportado | No se completó una adaptación; no afirmar que el backend actual se ejecutó allí |
| Vercel Functions | Runtime Python con FastAPI y dependencias declaradas en `pyproject.toml`/`uv.lock` | Elegido y desplegado sin Docker |

La elección inicial de Containers buscaba evitar adaptar dependencias nativas; no pretendía mover SQLite fuera de Turso. El usuario aclaró que quería desplegar la API, conservar sus proveedores y evitar esa suscripción. Vercel resultó una ruta compatible con la aplicación actual.

## Fuentes oficiales consultadas

| ID | Fuente y sección | Aplicación concreta |
| --- | --- | --- |
| F1 | [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi), entrada, dependencias, lifespan y Functions | Entrada `app.main:app`, sin wrappers HTTP adicionales |
| F2 | [Runtime Python](https://vercel.com/docs/functions/runtimes/python), versión y dependencias | Python 3.12, `pyproject.toml`, `uv.lock`, exclusiones de bundle |
| F3 | [GitHub Actions con Vercel](https://vercel.com/kb/guide/how-can-i-use-github-actions-with-vercel), producción y artefactos precompilados | pull → build → deploy prebuilt |
| F4 | [CLI Vercel](https://vercel.com/docs/cli), autenticación CI y comandos | CLI fijado, token por entorno, login de dispositivo |
| F5 | [Crear token](https://vercel.com/docs/rest-api/authentication/create-an-auth-token), `projectId` y `expiresAt` | Alcance de proyecto y vencimiento solicitados; la app OAuth impidió crearlo automáticamente |
| F6 | [Variables de proyecto](https://vercel.com/docs/rest-api/projects/create-one-or-more-environment-variables), upsert y entorno | Copia autorizada de valores al proyecto, secretos cifrados |
| F7 | [Vercel Hobby](https://vercel.com/docs/plans/hobby), límites y uso permitido | Cuenta gratuita para uso personal no comercial; no se contrató un plan |
| F8 | [Paquetes Python de Workers](https://developers.cloudflare.com/workers/languages/python/packages/), bibliotecas compatibles | Explica por qué no se asumió compatibilidad del controlador nativo |
| F9 | [FastAPI en Workers](https://developers.cloudflare.com/workers/languages/python/packages/fastapi/), ASGI | Confirma que el framework está soportado, sin demostrar compatibilidad de todas las dependencias del proyecto |
| F10 | [Precios de Containers](https://developers.cloudflare.com/containers/platform/pricing/), recursos y Workers Paid | Coste de la alternativa descartada |

Consulta de todas las fuentes: 2026-10-31. Las versiones efectivamente usadas constan en los workflows y lockfiles; las páginas de proveedor pueden cambiar.

## Límites de lo comprobado

Se comprobaron tests, empaquetado, despliegue, salud y rechazo de peticiones privadas sin sesión. Esas comprobaciones no sustituyen una sesión real de usuario en el frontend ni demuestran por sí solas todas las operaciones Turso/Blob. CORS y `azp` deben actualizarse con el dominio final del frontend; no usar comodines para resolver errores de conexión.

Este archivo conserva las decisiones del proyecto. Para futuras sesiones, leer primero el procedimiento, las configuraciones y el último workflow exitoso; no repetir intentos históricos como si fueran pasos necesarios.
