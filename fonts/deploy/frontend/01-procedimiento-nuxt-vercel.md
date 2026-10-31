# 01 — Nuxt en Vercel mediante GitHub Actions

Fecha de creación: 2026-10-31
Estado: Implementado y verificado
Relacionada con: [conexión y CORS](../backend/04-conectar-frontend-y-cors.md), [procedimiento backend](../backend/01-procedimiento-fastapi-vercel.md)

## Proyecto

- Equipo Vercel: `benjami-nofircials-projects`.
- Proyecto: `copilot-frontend`.
- Carpeta que se sube como raíz: `frontend/`.
- Producción: https://copilot-frontend-lovat.vercel.app
- Backend: https://copilot-backend-navy.vercel.app/api/v1

Fuentes: [Nuxt en Vercel](https://vercel.com/docs/frameworks/full-stack/nuxt), [GitHub Actions](https://vercel.com/kb/guide/how-can-i-use-github-actions-with-vercel), [Clerk y producción](https://clerk.com/docs/guides/development/deployment/production). Consulta: 2026-10-31.

## Configuración aplicada

Se sustituyó el preset de Cloudflare por `vercel` de Nitro y se retiró Wrangler. `frontend/vercel.json` selecciona `nuxtjs`, instala con el lockfile y ejecuta `pnpm build:vercel`. El `packageManager` fija pnpm `12.5.1`; `.node-version` fija Node `24.19.0` y el proyecto Vercel utiliza Node 24.

`scripts/require-deploy-env.mjs` detiene el build si falta la clave publicable, si se activa una sesión de preview o si la URL de API no es HTTPS pública con la ruta exacta `/api/v1`. El build de despliegue no carga `.env.local`; recibe sus variables desde Vercel.

Las claves Clerk existentes se copiaron con autorización explícita del usuario al entorno Production. No se creó otra instancia ni se cambiaron identidades. Las claves actuales son de desarrollo; el sitio desplegado sirve para probar la aplicación existente. Para promover Clerk a su instancia de producción se necesita un dominio propio y una etapa separada, porque cambiar la instancia cambia las identidades de usuario.

## Creación y despliegue inicial

```sh
npx --yes vercel@65.9.0 project create copilot-frontend --scope benjami-nofircials-projects
npx --yes vercel@65.9.0 link --cwd frontend --project copilot-frontend --scope benjami-nofircials-projects --yes
npx --yes vercel@65.9.0 deploy --cwd frontend --prod --yes --json
```

La CLI puede añadir `VERCEL_OIDC_TOKEN` al `.env.local` al vincular. Ese archivo permanece ignorado y no se copia completo a Vercel: solo se transfieren las variables de la aplicación elegidas. `.vercelignore` excluye entornos, dependencias y artefactos locales del upload.

El primer despliegue terminó en READY y proporcionó el alias estable de producción. Se usó ese alias para configurar CORS y `azp` en el backend, y se volvió a desplegar la API.

## GitHub Actions

Workflow: [deploy-frontend-vercel.yml](../../../.github/workflows/deploy-frontend-vercel.yml).

| Configuración del repositorio | Nombre |
| --- | --- |
| Variable compartida | `VERCEL_ORG_ID` |
| Variable del frontend | `VERCEL_FRONTEND_PROJECT_ID` |
| Secreto del frontend | `VERCEL_FRONTEND_TOKEN` |

El usuario creó y guardó el token separado del backend. El workflow ejecuta tipos y lint, obtiene las variables Production con `vercel pull`, compila con `vercel build --prod`, publica con `--prebuilt --prod --json` y verifica `/auth`. Los pushes de `frontend/` a `main` y la ejecución manual activan el flujo. `git.deploymentEnabled=false` evita publicar dos veces el mismo cambio mediante la integración Git nativa.

[Workflow completo verificado sobre `856d8a3`](https://github.com/benjamin12062006/copilot-voz/actions/runs/41177933101). [CI de ambos componentes](https://github.com/benjamin12062006/copilot-voz/actions/runs/41177933136) también terminó correctamente. Se consultó el equipo Vercel y se comprobó que su plan sigue siendo `hobby`; no se contrató una suscripción.

## Validación y errores observados

La compilación local para Vercel, el chequeo de tipos y lint terminaron correctamente. Inicialmente lint incluyó el bundle generado `.deploy-check` de una prueba anterior de Cloudflare; se retiró ese artefacto propio, sin cambiar las reglas del linter.

El navegador abrió la aplicación, recuperó la sesión de Clerk existente y llegó a `/session`. Tras publicar CORS y los orígenes autorizados del backend, completó esa etapa, llegó a `/home` y cargó la biblioteca existente. Las comprobaciones finales y sus resultados se conservan en la referencia de conexión enlazada.
