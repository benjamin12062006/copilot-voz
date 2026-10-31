# 21 — Cloudflare Workers y Containers

Fecha de creación: 2026-10-31
Tipo de fuente: documentación oficial y paquetes instalados
Fecha de consulta: 2026-10-31
Relacionada con: [guía](../deployment/01-cloudflare.md), [preparación](../../bitacora-construccion/backend/09-preparacion-cloudflare.md)

## Evidencia aplicada

- [Nuxt en Workers](https://developers.cloudflare.com/workers/framework-guides/web-apps/more-web-frameworks/nuxt/): Nuxt dispone de despliegue en Workers y recursos estáticos. En Nitro 2.13.4 instalado se comprobó el preset `cloudflare_module`; [referencia Nitro](https://nitro.build/deploy/providers/cloudflare).
- [Paquetes Python](https://developers.cloudflare.com/workers/languages/python/packages/): Python Workers requiere paquetes puros o compatibles con WebAssembly/Pyodide. El `libsql` bloqueado en el proyecto tiene wheels nativos; se elige Container Linux para conservar el backend sin reescribir su acceso a datos.
- [Introducción a Containers](https://developers.cloudflare.com/containers/get-started/): imagen Linux amd64, Worker y Durable Object para dirigir peticiones. La aplicación usa la API de `Container` y su política predeterminada.
- [Clase Container](https://developers.cloudflare.com/containers/api/container-class/): propiedades `defaultPort`, `sleepAfter`, `envVars` y `enableInternet`; envío de peticiones a una instancia con nombre.
- [Despliegue de Containers](https://developers.cloudflare.com/containers/guides/deploy/): Workers Builds puede construir el Dockerfile. `wrangler deploy` actualiza imagen y Worker; `versions upload` no despliega una imagen nueva. Un deploy no es una transacción entre ambos componentes.
- [Configuración de Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/configuration/): directorio raíz por componente y separación entre variables de compilación y ejecución.
- [Imagen de compilación](https://developers.cloudflare.com/workers/ci-cd/builds/build-image/): selección de Node y pnpm mediante archivos de versión y `packageManager`.
- [Precios de Containers](https://developers.cloudflare.com/containers/platform/pricing/): requiere Workers Paid y factura recursos activos. La preparación no activa una suscripción.

## Adaptación y límites

Se conservan las rutas y autenticación de FastAPI. Un Worker pequeño pasa una lista explícita de configuración al contenedor y dirige todas las peticiones a una sola instancia. Las variables adicionales del panel se conservan con `keep_vars`; las declaradas en `vars` pertenecen al repositorio. Las credenciales nunca se incorporan a la imagen.

La decisión no demuestra por sí misma que exista un despliegue: el panel debe conectarse al repositorio y recibir los secretos. Las comprobaciones ejecutadas se registran en la bitácora.
