# 03 — Frontend Nuxt en Vercel y conexión a FastAPI

Fecha de creación: 2026-10-31
Estado: Desplegado y conexión verificada; validación de Actions en curso
Ámbito: frontend y configuración entre servicios
Relacionada con: [antecedente](02-conexion-api-perfil-mcp-y-voz-en-vivo.md), [backend Vercel](../backend/10-fastapi-vercel-y-actions.md), [procedimiento](../../fonts/deploy/frontend/01-procedimiento-nuxt-vercel.md), [URLs y CORS](../../fonts/deploy/backend/04-conectar-frontend-y-cors.md)
Revisión de partida: `aa5694c`

El usuario pidió conservar toda la investigación de backend en `fonts/deploy/backend` y seguir con el frontend, actualizando las URLs y los controles de origen de ambos. Se añadieron cuatro archivos de memoria de backend y el procedimiento del frontend, con fuentes, comandos, fallos y comprobaciones verificables.

Se creó y configuró `copilot-frontend` en Vercel con el preset Nuxt/Nitro `vercel`; se retiró la configuración Workers. El build exige la clave publicable, una API HTTPS pública y preview desactivado. Se agregaron exclusiones de upload y un workflow separado con credencial propia para el frontend.

El usuario autorizó copiar sus claves Clerk existentes a Vercel y guardó `VERCEL_FRONTEND_TOKEN` directamente en GitHub. La clave secreta permanece fuera del HTML y del repositorio. El frontend apunta a `https://copilot-backend-navy.vercel.app/api/v1`.

El alias resultante `https://copilot-frontend-lovat.vercel.app` se añadió a CORS y a `CLERK_AUTHORIZED_PARTIES` del backend, conservando los orígenes locales. Se comprobó que la clave publicable corresponde al mismo issuer del backend. Se volvió a publicar la API mediante Actions para aplicar los valores.

El prompt MCP que se copia desde Perfil usa ahora `window.location.origin` para describir la interfaz abierta, junto a la URL API de configuración. Así, las instrucciones copiadas desde producción dejan de dirigir al agente al frontend local.

Comprobaciones: tipos, lint y build Nuxt correctos; frontend HTTP 200; preflight permitido 200 y ajeno 400; navegador con sesión real llegó a Inicio y cargó la biblioteca existente. No se crearon documentos ni se ejecutaron migraciones durante esta validación. Pendiente de cerrar la comprobación del workflow del frontend sobre la versión publicada.
