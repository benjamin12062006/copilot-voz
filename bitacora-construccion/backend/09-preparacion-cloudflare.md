# 09 — Preparar frontend y backend para Cloudflare

Fecha de creación: 2026-10-31
Estado: Implementado y verificado (preparación; sin despliegue)
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

La imagen Docker se construyó y arrancó correctamente en el runner Linux amd64 de GitHub; `/health` respondió y se verificó la ausencia de `/app/.env`. Docker local no estaba iniciado; no fue necesario iniciarlo para completar la validación remota.

La primera ejecución de CI detectó que `DocumentStore.list` ocultaba el builtin `list` al evaluar una anotación posterior en Python 3.12. Se añadió `from __future__ import annotations` a `app/documents.py` para aplazar esa evaluación, sin cambiar métodos ni contratos. Las 29 pruebas pasaron después tanto en el entorno local como en Linux/Python 3.12.

[CI verificada sobre `3b08882`](https://github.com/benjamin12062006/copilot-voz/actions/runs/41175716737): ambos jobs correctos, incluido build de Nuxt y empaquetado de Workers. Tras la aclaración del usuario se conserva el namespace existente `copilot/dev`; no se añade almacenamiento en Cloudflare ni se modifica Turso. El Durable Object de configuración solo administra el ciclo de vida del contenedor FastAPI.

La suscripción, conexión del repositorio, secretos de Cloudflare y despliegue real quedan fuera de esta preparación. El Worker frontend previamente creado seguía teniendo únicamente Hello World al comenzar este incremento.
