# 09 — Preparar frontend y backend para Cloudflare

Fecha de creación: 2026-10-31
Estado: En curso
Ámbito: publicación del repositorio y configuración de despliegue
Relacionada con: [antecedente](08-retencion-borrado-y-migracion-turso.md), [fuentes](../../docs/fonts/21-cloudflare-workers-y-containers.md), [guía](../../docs/deployment/01-cloudflare.md)
Revisión de partida: `3b236c7`

## Solicitud y decisión

Guardar y publicar el estado existente en un repositorio público nuevo, y preparar todo lo necesario para vincularlo posteriormente a Cloudflare. Se publicó primero el checkpoint `3b236c7` en `benjamin12062006/copilot-voz`, rama `main`.

Nuxt se empaqueta para Workers. FastAPI utiliza Containers para conservar `libsql` nativo sin cambiar contratos de aplicación. La decisión se basa en las [fuentes oficiales](../../docs/fonts/21-cloudflare-workers-y-containers.md).

## Implementación

- Wrangler y lockfiles separados para `frontend/` y `backend/`.
- Imagen Python Linux amd64 con contexto Docker limitado al código y dependencias; sin `.env`, configuración de editores ni clientes MCP.
- Worker `CopilotApi` con variables explícitas, una instancia y suspensión por inactividad.
- Valores públicos de URLs, CORS y entorno declarados en Wrangler; plantillas vacías de secretos.
- Build del frontend que exige la clave publicable de Clerk y rechaza sesiones de preview.
- CI de GitHub que valida sin secretos reales y prueba la imagen Docker.
- Guía de conexión mediante Workers Builds, que evita un segundo sistema de despliegue y tokens de Cloudflare en GitHub.

## Verificación

Antes de configurar infraestructura: tipos y lint del frontend correctos; 29 pruebas del backend correctas. Revisión del historial Git sin coincidencias con credenciales locales ni patrones de claves privadas/token examinados. Solo se publicaron plantillas de entorno.

Tipos del Worker backend, compilación del frontend con Clerk sintético y empaquetado de ambos Workers con `wrangler deploy --dry-run`: correctos. El empaquetado backend usa `--containers-rollout=none` para comprobar el Worker sin necesitar Docker. La imagen se prueba separadamente en CI.

Pendiente de comprobar la imagen Docker en el runner Linux de GitHub. Docker local no estaba iniciado y no se obtuvo acceso de Computer Use a OrbStack.

La suscripción, conexión del repositorio, secretos de Cloudflare y despliegue real quedan fuera de esta preparación. El Worker frontend previamente creado seguía teniendo únicamente Hello World al comenzar este incremento.
