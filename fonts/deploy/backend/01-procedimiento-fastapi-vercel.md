# 01 — Procedimiento comprobado: FastAPI en Vercel mediante GitHub Actions

Fecha de creación: 2026-10-31
Estado: Implementado y verificado
Relacionada con: [fuentes](02-investigacion-y-decisiones.md), [problemas resueltos](03-errores-y-soluciones.md), [guía del proyecto](../../../docs/deployment/02-vercel-backend.md), [bitácora](../../../bitacora-construccion/backend/10-fastapi-vercel-y-actions.md)
Revisiones: `4525811` antes de la migración, `c46afcc` configuración Vercel, `aa5694c` corrección del bundle precompilado.

## Resultado real

| Elemento | Valor |
| --- | --- |
| Cuenta GitHub | `benjamin12062006` |
| Repositorio público | `benjamin12062006/copilot-voz` |
| Rama de producción | `main` |
| Equipo Vercel | `benjami-nofircials-projects` |
| Proyecto | `copilot-backend` |
| Producción | https://copilot-backend-navy.vercel.app |
| Entrada | `app.main:app` |
| Runtime | Python 3.12 |
| Carpeta que se sube como raíz | `backend/` |

[Ejecución completa de Actions verificada](https://github.com/benjamin12062006/copilot-voz/actions/runs/41177318309): pruebas, descarga de configuración, build Linux, publicación prebuilt y salud correctos. `GET /health` devuelve `200 {"status":"ok"}`. Las rutas privadas sin sesión responden 401.

## 1. Comprobar y guardar el punto de partida

Leer instrucciones del repositorio y revisar rama, cambios, tags, remotos y archivos no rastreados. Se publicó primero el proyecto existente en un repositorio público nuevo y se excluyeron los `.env` y las credenciales. Se conservaron las versiones históricas `v0.1.0`, `v0.2.0` y `v0.3.0`; la migración de proveedor no alteró esos tags.

Antes de publicar, se compararon los archivos rastreados y el historial con los secretos locales y patrones de credenciales, mostrando únicamente nombres de archivo y tipo de coincidencia, nunca sus valores. Esta revisión no sustituye la rotación si alguna credencial se filtrara por otro medio.

## 2. Configurar FastAPI para Vercel

Se conservó el código de la API. `backend/pyproject.toml` declara:

```toml
[tool.vercel]
entrypoint = "app.main:app"
```

`.python-version` contiene `3.12`. Esa versión tiene un wheel compatible del controlador `libsql` y pasó las 29 pruebas tanto en macOS como en Linux.

[`vercel.json`](../../../backend/vercel.json) selecciona `fastapi`, limita cada petición a 60 segundos y excluye archivos locales del bundle. No se usa Docker, D1 ni una base SQLite local de producción. Turso y Upstash Blob conservan su función y sus datos.

La carpeta raíz configurada en el proyecto Vercel es nula porque el CLI se ejecuta dentro de `backend/` y sube esa carpeta como raíz. No configurar además `rootDirectory=backend` en este flujo: duplicaría el desplazamiento. Si se eligiera la integración Git nativa con la raíz del monorepo, la configuración sería diferente.

## 3. Usar una versión actual del CLI y autenticar

Versión usada: Vercel CLI `65.9.0`. El CLI global previo era `37.14.0`; se instaló el actual en una carpeta temporal para evitar depender de esa versión antigua.

Comandos reproducibles:

```sh
npx --yes vercel@65.9.0 whoami
npx --yes vercel@65.9.0 login
npx --yes vercel@65.9.0 project create copilot-backend --scope benjami-nofircials-projects
npx --yes vercel@65.9.0 link --cwd backend --project copilot-backend --scope benjami-nofircials-projects --yes
```

En esta sesión se utilizó el comando anterior `project add`, todavía aceptado; el CLI actual recomienda `project create`. `login` mostró una URL y un código de dispositivo que el usuario aprobó. No guardar códigos de autenticación, tokens de sesión o archivos `auth.json` en esta documentación.

## 4. Configurar las variables sin publicarlas

Después de recibir autorización explícita se copiaron al entorno Production de Vercel los valores existentes de Turso, Blob y Clerk. Solo se utilizaron las variables que consume el backend. No se copió la variable antigua `COPILOT_STORAGE_API_TOKEN`.

| Variable | Uso |
| --- | --- |
| `TURSO_DATABASE_URL` | destino de la base existente |
| `TURSO_AUTH_TOKEN` | secreto cifrado en Vercel |
| `UPSTASH_BLOB_TOKEN` | secreto cifrado en Vercel |
| `CLERK_ISSUER` | misma instancia usada por el frontend |
| `COPILOT_ENV` | `production` |
| `COPILOT_CORS_ORIGINS` | lista JSON de orígenes exactos del frontend |
| `CLERK_AUTHORIZED_PARTIES` | lista JSON de orígenes autorizados en los JWT |
| `COPILOT_STORAGE_NAMESPACE` | `copilot/dev`, valor existente |
| `COPILOT_STORAGE_MAX_DOCUMENT_BYTES` | `1048576` |
| `UPSTASH_DISABLE_TELEMETRY` | `true` |

El API de Vercel usado fue `POST /v10/projects/{id}/env?upsert=true`, con `target=["production"]` y `type=encrypted` para los tokens. Los valores se leyeron en memoria desde el `.env` local y nunca se imprimieron en logs ni se escribieron en el repositorio.

Al desplegar el frontend, actualizar `COPILOT_CORS_ORIGINS` y `CLERK_AUTHORIZED_PARTIES` con su URL real, volver a desplegar el backend y verificar preflight. Cambiar variables en el panel no actualiza las funciones ya desplegadas.

## 5. Configurar GitHub Actions

En el repositorio:

| Configuración | Nombre |
| --- | --- |
| Actions variable | `VERCEL_ORG_ID` |
| Actions variable | `VERCEL_BACKEND_PROJECT_ID` |
| Actions secret | `VERCEL_BACKEND_TOKEN` |

El usuario creó el token en el panel Vercel y lo guardó directamente en GitHub. La sesión OAuth del CLI no permite crear tokens personales. Se pidió alcance limitado al proyecto y vencimiento de un año. No sustituirlo por la sesión personal general del CLI.

El [workflow](../../../.github/workflows/deploy-backend-vercel.yml) se ejecuta en `ubuntu-24.04` al cambiar `backend/` en `main`, al cambiar el propio workflow o manualmente. Usa permisos `contents: read` y evita despliegues simultáneos. Las PR no reciben secretos de producción.

Secuencia:

1. Instalar Python 3.12/dependencias con `uv 0.12.1` y `uv.lock`.
2. Ejecutar las 29 pruebas existentes.
3. Instalar Vercel CLI `65.9.0`.
4. `vercel pull --yes --environment=production`.
5. `vercel build --prod`.
6. `vercel deploy --prebuilt --prod --json`.
7. Extraer la URL de producción del JSON y comprobar `/health`.

`VERCEL_TOKEN` se entrega como variable de entorno del job; no se añade a argumentos de procesos. Los binarios se compilan/instalan en Linux antes de usar `--prebuilt`. `git.deploymentEnabled=false` evita duplicar despliegues con la integración Git nativa.

## 6. Comprobar y operar

```sh
curl --fail https://copilot-backend-navy.vercel.app/health
gh workflow run deploy-backend-vercel.yml --repo benjamin12062006/copilot-voz --ref main
gh run list --repo benjamin12062006/copilot-voz --workflow deploy-backend-vercel.yml
```

El primer despliegue se realizó con el CLI y después se verificó el mismo proceso desde Actions. La prueba de salud comprueba el arranque, no la conexión a todos los proveedores. Las pruebas de despliegue no ejecutan migraciones ni crean documentos. Las migraciones siguen siendo una operación separada y explícita.

Los clientes MCP conservan su proceso stdio local y usan `COPILOT_API_BASE_URL=https://copilot-backend-navy.vercel.app/api/v1`. Su token personal de documentos es distinto del token de despliegue Vercel.
