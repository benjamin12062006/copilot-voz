# 01 — Conectar Copilot a Cloudflare

Fecha de creación: 2026-10-31
Estado: configuración del repositorio; conexión y despliegue pendientes
Actualización 2026-10-31: la opción Containers del backend fue sustituida por [FastAPI en Vercel](02-vercel-backend.md). Este documento conserva la configuración histórica; sus pasos de backend ya no deben ejecutarse. El frontend continúa preparado para Workers.
Relacionada con: [fuentes oficiales](../fonts/21-cloudflare-workers-y-containers.md), [preparación](../../bitacora-construccion/backend/09-preparacion-cloudflare.md)
Revisión de partida: `3b236c7` (estado previo a configurar Cloudflare).

## Arquitectura preparada

El frontend Nuxt se compila con el preset `cloudflare_module` del Nitro instalado. El backend FastAPI conserva su código y dependencias Python dentro de un Container Linux amd64, detrás de un Worker. La clase `CopilotApi` pasa explícitamente las variables y secretos del Worker al proceso Python; Cloudflare no los transfiere automáticamente al contenedor.

Se usa una instancia `basic`, con un máximo de una instancia y suspensión tras dos minutos de inactividad. Turso y Blob conservan los datos fuera del disco efímero. La primera petición después de la suspensión puede tardar mientras arranca Python.

Containers necesita **Workers Paid**, que parte de USD 5 al mes más el consumo aplicable. Preparar y subir estos archivos no activa ese plan. Revisar [precios oficiales](https://developers.cloudflare.com/containers/platform/pricing/) antes del despliegue.

## Vincular GitHub mediante Workers Builds

Repositorio: https://github.com/benjamin12062006/copilot-voz

1. Ir a **Compute → Workers & Pages**.
2. Para el frontend, abrir el Worker existente `copilot-frontend` y entrar en **Settings → Build(s) → Connect Git**. Elegir el repositorio anterior y la rama `main`.
3. Para el backend, crear/conectar un Worker llamado `copilot-backend` al mismo repositorio. El nombre debe coincidir con `backend/wrangler.jsonc`.
4. Aplicar los valores de la tabla. Guardar las variables antes de lanzar o reintentar la primera compilación.

| Ajuste | Frontend | Backend |
| --- | --- | --- |
| Rama de producción | `main` | `main` |
| Root directory | `frontend` | `backend` |
| Build command | `pnpm build:cloudflare` | `pnpm typecheck:cloudflare` |
| Deploy command | `pnpm deploy:cloudflare` | `pnpm deploy:cloudflare` |
| Instalación | detección automática con `pnpm-lock.yaml` | detección automática con `pnpm-lock.yaml` |
| NODE_VERSION, si se pide | `24.19.0` | `24.19.0` |
| PNPM_VERSION, si se pide | `12.5.1` | `12.5.1` |

`packageManager` fija pnpm en ambos componentes; `frontend/.node-version` fija Node para Nuxt. Wrangler está instalado como dependencia local, por lo que no hace falta instalarlo globalmente.

El backend compila su Dockerfile durante `wrangler deploy` dentro de Workers Builds. Desactivar compilaciones de ramas de prueba inicialmente para este servicio: `wrangler versions upload` no actualiza imágenes ni proporciona una vista previa completa de Containers. Usar otro Worker con configuración y recursos propios si después se necesita staging.

No hace falta copiar un token de Cloudflare a GitHub para esta integración: Workers Builds gestiona la autenticación del despliegue. El workflow de GitHub incluido ejecuta validaciones, sin publicar la aplicación.

## Variables del frontend

En **Settings → Build(s) → Variables and secrets**, agregar:

| Nombre | Tipo | Valor |
| --- | --- | --- |
| `NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Text | clave publicable de la instancia elegida |
| `NUXT_PUBLIC_CLERK_KEYLESS_DISABLED` | Text | `true` |
| `NUXT_PUBLIC_PREVIEW_SESSION` | Text | `false` |

La clave publicable debe existir durante la compilación porque `nuxt.config.ts` decide entonces si registra el módulo Clerk. El script detiene la compilación si falta. No usar la clave sintética de CI para un despliegue real.

En **Settings → Variables and Secrets** del Worker frontend, agregar:

| Nombre | Tipo | Valor |
| --- | --- | --- |
| `NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Text | misma clave publicable de la compilación |
| `NUXT_CLERK_SECRET_KEY` | Secret | clave secreta de esa misma instancia |

Estas variables de ejecución son distintas de las de compilación. La clave secreta permanece en el servidor; nunca lleva el prefijo `NUXT_PUBLIC_`.

`frontend/wrangler.jsonc` ya declara la URL del backend, `DATA_SOURCE=api`, keyless desactivado y preview desactivado. `keep_vars: true` conserva las variables adicionales guardadas en el panel; los valores explícitos de `vars` se administran desde el archivo. Si cambia el dominio, editar las URLs versionadas y volver a desplegar.

Plantilla completa: [`frontend/.env.production.example`](../../frontend/.env.production.example).

## Variables del backend

En **Settings → Variables and Secrets** del Worker backend, agregar:

| Nombre | Tipo | Valor |
| --- | --- | --- |
| `CLERK_ISSUER` | Text | origen HTTPS de la instancia Clerk usada por el frontend |
| `TURSO_DATABASE_URL` | Text | URL `libsql://…` de la base elegida |
| `TURSO_AUTH_TOKEN` | Secret | token de esa base |
| `UPSTASH_BLOB_TOKEN` | Secret | token del bucket elegido |
| `COPILOT_ALLOWED_CLERK_USER_IDS` | Text, opcional | lista JSON de usuarios permitidos, p. ej. `["user_…"]` |
| `CLERK_JWT_KEY` | Secret, opcional | clave de verificación si se usa verificación local |
| `CLERK_SECRET_KEY` | Secret, opcional | solo si alguna funcionalidad llega a requerirla |

Ya están declarados en `backend/wrangler.jsonc`:

```text
COPILOT_ENV=production
COPILOT_CORS_ORIGINS=["https://copilot-frontend.benjamin12062006.workers.dev"]
CLERK_AUTHORIZED_PARTIES=["https://copilot-frontend.benjamin12062006.workers.dev"]
COPILOT_STORAGE_NAMESPACE=copilot/dev
COPILOT_STORAGE_MAX_DOCUMENT_BYTES=1048576
```

Se conserva `copilot/dev`, el espacio que ya utiliza el proyecto, para mantener el acceso a sus documentos existentes. El despliegue no crea una base SQLite local ni configura almacenamiento en Cloudflare. Turso y Upstash Blob siguen siendo los proveedores existentes.

Al cambiar secretos, reiniciar el contenedor para que el nuevo proceso reciba los valores; también puede dejarse que se suspenda tras dos minutos sin tráfico y comprobar el siguiente arranque. No añadir `COPILOT_STORAGE_API_TOKEN`: es una variable antigua que el backend actual no consume. Los tokens MCP son personales y se generan en la aplicación.

Plantilla para desarrollo con Wrangler: [`backend/.dev.vars.example`](../../backend/.dev.vars.example). Copiar a `.dev.vars` únicamente en el equipo local; el archivo real se ignora en Git y Docker.

## Clerk y migraciones antes de abrir la aplicación

Las credenciales locales actuales de Clerk son de desarrollo. Para publicar en producción, configurar la instancia de producción, sus dominios autorizados y sus claves. Clerk requiere un dominio propio con acceso a DNS para producción; las URLs `workers.dev` de esta preparación sirven como punto de partida para pruebas. Al elegir el dominio definitivo, actualizar las URLs y CORS de ambos archivos Wrangler. Véase la [guía oficial de Clerk](https://clerk.com/docs/guides/development/deployment/production).

Las claves publicable y secreta y `CLERK_ISSUER` deben pertenecer a la misma instancia. Cambiar de instancia cambia la identidad de los usuarios; los perfiles existentes no se migran por copiar variables.

El despliegue usa la base Turso existente. No crea otra base ni aplica migraciones. Para comprobar el esquema actual desde `backend/`, sin modificarlo:

```sh
uv run --locked python -m app.migrations
uv run --locked python -m app.database
```

Sin `--apply`, el comando de migraciones solo valida el esquema. El servidor no ejecuta DDL al arrancar. Cualquier migración futura debe tratarse aparte del despliegue.

## CLI opcional y verificación posterior

Para usar la integración nativa, basta el navegador. Para trabajar por CLI:

```sh
cd frontend
pnpm install --frozen-lockfile
pnpm exec wrangler login
```

Para compilar localmente, copiar `.env.production.example` a `.env.production`, completar la clave publicable y exportar sus variables antes de `pnpm build:cloudflare`. La clave secreta se configura como secret de ejecución, no hace falta incluirla en el build.

```sh
set -a
source .env.production
set +a
pnpm build:cloudflare
pnpm check:cloudflare
pnpm deploy:cloudflare
```

Para el backend, desde `backend/`, instalar con `pnpm install --frozen-lockfile`, iniciar Docker y ejecutar `pnpm deploy:cloudflare`. Workers Builds evita necesitar Docker en la computadora.

Después de desplegar, esperar el aprovisionamiento inicial y comprobar:

1. `GET https://copilot-backend.benjamin12062006.workers.dev/health` devuelve `{"status":"ok"}`.
2. El frontend carga, permite iniciar sesión y obtiene el perfil.
3. Crear, listar, escuchar y eliminar un documento prueba Clerk, Turso y Blob; `/health` solo prueba el proceso.
4. Crear un token MCP personal y configurar el cliente con la URL HTTPS del backend. El servidor MCP sigue ejecutándose por stdio en el cliente; no es otro servicio HTTP que se publique en Cloudflare.

GitHub Actions comprueba tipos, lint, build de Nuxt para Workers, empaquetado de Wrangler, las pruebas del backend y el arranque de la imagen Docker sin credenciales de proveedores. La conexión real a Cloudflare, Clerk, Turso y Blob se verifica después de configurar los secretos y desplegar.
