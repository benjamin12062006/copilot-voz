# 22 — Vercel FastAPI y GitHub Actions

Fecha de creación: 2026-10-31
Tipo de fuente: documentación oficial
Fecha de consulta: 2026-10-31
Relacionada con: [guía](../deployment/02-vercel-backend.md), [bitácora](../../bitacora-construccion/backend/10-fastapi-vercel-y-actions.md)

## Evidencia aplicada

- [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi): `app/main.py` es una entrada reconocida y `tool.vercel.entrypoint` permite declararla explícitamente. FastAPI se ejecuta como Vercel Function y admite lifespan.
- [Runtime Python](https://vercel.com/docs/functions/runtimes/python): versiones 3.12, 3.13 y 3.14; admite `pyproject.toml` y `uv.lock`. Se fija 3.12 porque esa combinación ya pasó las pruebas Linux del proyecto y dispone de wheel `libsql`.
- [GitHub Actions con Vercel](https://vercel.com/kb/guide/how-can-i-use-github-actions-with-vercel): `pull`, `build --prod`, `deploy --prebuilt --prod`; evita repetir el build al publicar los mismos artefactos.
- [Crear token](https://vercel.com/docs/rest-api/authentication/create-an-auth-token): `projectId` limita el alcance y `expiresAt` establece vencimiento. Se usa un secreto de GitHub separado de la sesión personal.
- [Variables de proyecto](https://vercel.com/docs/rest-api/projects/create-one-or-more-environment-variables): valores por entorno, secretos cifrados y upsert.
- [Vercel Hobby](https://vercel.com/docs/plans/hobby): uso personal no comercial y límites de recursos. La preparación no contrata un plan de pago.

## Decisión

Se reemplaza Containers por el runtime Python nativo de Vercel para ejecutar la aplicación actual sin Docker ni adaptar todo su acceso a datos al entorno WebAssembly de Workers. Se conservan FastAPI, Turso/libSQL, Clerk y Blob. GitHub Actions es el único flujo de despliegue elegido.
