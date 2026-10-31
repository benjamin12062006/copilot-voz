# 10 — FastAPI en Vercel y despliegue desde GitHub Actions

Fecha de creación: 2026-10-31
Estado: Backend desplegado; automatización pendiente de credencial del usuario
Ámbito: despliegue del backend
Relacionada con: [antecedente](09-preparacion-cloudflare.md), [guía](../../docs/deployment/02-vercel-backend.md), [fuentes](../../docs/fonts/22-vercel-fastapi-y-github-actions.md)
Revisión de partida: `4525811`

## Solicitud y decisión

El usuario eligió Vercel y pidió crear el proyecto por terminal, autenticar lo necesario y usar GitHub Actions, empezando por el backend. Se conserva el frontend para otra etapa.

Se creó `copilot-backend` bajo el equipo existente y se vinculó `backend/`. FastAPI usa el runtime nativo Python 3.12 y la entrada `app.main:app`. Se retiraron Docker y el adaptador Containers del backend. No se modifican los datos ni los contratos HTTP.

## Configuración

- `vercel.json`: framework FastAPI, duración máxima de 60 segundos y exclusión de archivos locales.
- `pyproject.toml`: entrada explícita; `.python-version`: 3.12.
- `.vercelignore` y `.gitignore`: credenciales fuera del código y del repositorio.
- CI valida el arranque directamente con uvicorn, sin Docker.
- Workflow de producción: pruebas → pull → build Linux → deploy prebuilt → salud.

Se guardaron las variables existentes de Turso, Blob y Clerk en Vercel Production después de la autorización explícita del usuario. Se mantiene el namespace existente. La revisión automática inicialmente exigió esta autorización para transferir secretos; no se ejecutó esa transferencia hasta recibirla.

## Verificación en curso

Las 29 pruebas pasaron en un entorno temporal Python 3.12. La sesión del CLI se renovó con el flujo oficial de dispositivo y se verificó la misma cuenta. El proyecto tiene framework FastAPI y el primer despliegue de producción terminó en estado READY.

URL: https://copilot-backend-navy.vercel.app. `GET /health` devuelve 200 y `{"status":"ok"}` sin autenticación de Vercel en el dominio de producción. No se ejecutaron migraciones ni se modificaron datos para verificarlo.

`GET /api/v1/auth/me` y `GET /api/v1/documents` sin credenciales devuelven 401 con el contrato de error existente. `vercel build --prod` también terminó correctamente en el equipo local; el workflow usa ese mismo comando en Linux antes de publicar artefactos precompilados. Se revisaron los archivos publicables y no contienen coincidencias con los secretos locales; `.vercel/` permanece ignorado.

Vercel impide crear tokens personales desde la aplicación OAuth del CLI (`Cannot create tokens for this app`). Se solicitó al usuario crear un token en el panel, limitado al proyecto, y guardarlo como secreto `VERCEL_BACKEND_TOKEN` del repositorio. Los IDs ya están guardados como variables GitHub. No se reutilizó la sesión personal general como credencial de CI.

Pendiente: guardar ese token y ejecutar el workflow de producción completo. No se publican valores secretos en este documento.
