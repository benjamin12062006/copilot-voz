# 02 — FastAPI en Vercel con GitHub Actions

Fecha de creación: 2026-10-31
Estado: backend desplegado y verificado; credencial de GitHub Actions pendiente
Relacionada con: [fuentes oficiales](../fonts/22-vercel-fastapi-y-github-actions.md), [bitácora](../../bitacora-construccion/backend/10-fastapi-vercel-y-actions.md), [opción anterior](01-cloudflare.md)
Revisión de partida: `4525811`

## Proyecto y alcance

- Vercel: `benjami-nofircials-projects/copilot-backend`.
- Repositorio: `benjamin12062006/copilot-voz`, rama `main`.
- Código desplegado: carpeta `backend/`, subida como raíz del proyecto.
- Entrada: `app.main:app`, declarada en `pyproject.toml`.
- Runtime: Python 3.12, fijado en `.python-version` por compatibilidad con los wheels nativos de `libsql`.
- URL de producción: https://copilot-backend-navy.vercel.app
- Salud verificada: `GET /health` → `200 {"status":"ok"}`.

El frontend se atiende después. Se eliminó la infraestructura de Containers del backend: Dockerfile, Worker TypeScript, Durable Object y dependencias Node de ese adaptador. Turso y Blob no se trasladan ni se migran.

Vercel Hobby permite uso personal no comercial, sujeto a sus cuotas. El proyecto no necesita contratar Cloudflare Workers Paid.

## Autenticación y variables

El proyecto se creó por CLI usando la sesión existente del usuario. Vercel puede exigir `vercel login` para renovar la sesión antes de acceder a variables o crear credenciales.

Las siguientes variables se configuran en el entorno Production de Vercel, manteniendo los valores del proyecto local:

| Variable | Tipo |
| --- | --- |
| `TURSO_DATABASE_URL` | Configuración |
| `TURSO_AUTH_TOKEN` | Secreto cifrado |
| `UPSTASH_BLOB_TOKEN` | Secreto cifrado |
| `CLERK_ISSUER` | Configuración |
| `COPILOT_ENV` | `production` |
| `COPILOT_CORS_ORIGINS` | Lista JSON de orígenes exactos |
| `CLERK_AUTHORIZED_PARTIES` | Lista JSON de orígenes exactos |
| `COPILOT_STORAGE_NAMESPACE` | `copilot/dev`, espacio existente |
| `COPILOT_STORAGE_MAX_DOCUMENT_BYTES` | `1048576` |
| `UPSTASH_DISABLE_TELEMETRY` | `true` |

Los orígenes actuales permiten el frontend local. Al desplegar el frontend, añadir su origen HTTPS a las dos listas y volver a desplegar el backend. No usar `*` ni cambiar la instancia Clerk al conectar el backend: debe verificar los tokens de la instancia existente.

`backend/.env` permanece local. `.vercelignore` y `excludeFiles` excluyen credenciales y configuración de clientes MCP del código enviado y del bundle. `.vercel/` se ignora en Git, incluidos los archivos descargados por `vercel pull`.

## GitHub Actions

Workflow: [deploy-backend-vercel.yml](../../.github/workflows/deploy-backend-vercel.yml).

Se ejecuta al subir cambios de `backend/` a `main`, al cambiar el workflow o manualmente con `workflow_dispatch`. Las pull requests solo ejecutan CI; no reciben secretos de producción.

Configurar en el repositorio GitHub:

| Nombre | Ubicación | Valor |
| --- | --- | --- |
| `VERCEL_ORG_ID` | Actions variable | identificador del equipo Vercel |
| `VERCEL_BACKEND_PROJECT_ID` | Actions variable | identificador de `copilot-backend` |
| `VERCEL_BACKEND_TOKEN` | Actions secret | token limitado al proyecto, con duración de un año |

No reutilizar el token personal general del CLI como secreto del repositorio. La credencial de automatización debe estar limitada al proyecto. Rotarla antes de su vencimiento.

La sesión OAuth del CLI permite desplegar pero devuelve `Cannot create tokens for this app` al intentar generar una credencial personal. Crear el token en [Vercel](https://vercel.com/account/settings/tokens) y guardarlo directamente en GitHub como `VERCEL_BACKEND_TOKEN`, sin pegarlo en el chat. Los identificadores del equipo y proyecto ya están guardados como variables del repositorio.

El workflow valida las 29 pruebas del backend antes de ejecutar la secuencia oficial:

```sh
vercel pull --yes --environment=production
vercel build --prod
vercel deploy --prebuilt --prod
```

Los artefactos se compilan en Linux dentro del runner; no se suben binarios macOS como artefactos precompilados. La configuración `git.deploymentEnabled=false` impide duplicar despliegues mediante la integración Git nativa si se conecta posteriormente. El CLI está fijado a `65.9.0`.

Los comandos leen `VERCEL_TOKEN` desde el entorno del job. El secreto no se agrega a los argumentos de la línea de comandos.

## Operación desde terminal

Para vincular otra copia local:

```sh
cd backend
npx --yes vercel@65.9.0 login
npx --yes vercel@65.9.0 link --project copilot-backend --scope benjami-nofircials-projects
```

Para lanzar el workflow ya configurado:

```sh
gh workflow run deploy-backend-vercel.yml --repo benjamin12062006/copilot-voz --ref main
```

`GET /health` comprueba que FastAPI arrancó. Una ruta privada sin sesión válida debe devolver 401. Las comprobaciones de despliegue no ejecutan migraciones ni crean documentos. Para verificar Turso sin modificar datos se puede ejecutar el comando existente `python -m app.database` con las variables del entorno elegido.

Los clientes MCP conservan el proceso stdio local y cambian únicamente `COPILOT_API_BASE_URL` a la URL HTTPS del backend terminado en `/api/v1`; sus tokens personales no son el token de Vercel.
