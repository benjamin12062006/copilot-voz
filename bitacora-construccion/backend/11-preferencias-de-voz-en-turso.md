# 11 — Preferencia de lectura automática en Turso

Fecha de creación: 2026-10-31
Estado: Implementado y verificado
Ámbito: backend FastAPI, Turso y frontend
Relacionada con: [frontend 04](../frontend/04-lectura-automatica-localhost.md), [plan frontend 07](../../docs/plans/frontend/07-lectura-automatica.md), [retención en Turso](08-retencion-borrado-y-migracion-turso.md)
Revisión de partida: `d5c781b`

## Solicitud

El usuario probó en localhost la lectura automática guardada en el navegador y confirmó que funcionaba. Pidió llevar la opción a la base de datos, sincronizar el backend y desplegar por el medio más prudente.

## Qué se hizo

- **Migración `004_voice_preferences.sql`.**
  - Crea la tabla `app_voice_preferences`: `user_id` es la clave primaria y referencia a `app_users`; `auto_read_mode` admite solo `off`, `agent` o `all`.
  - `migrations.py` la registra, comprueba su esquema y la añade a las tablas permitidas, con el mismo patrón que la 003.
- **`app/voice_preferences.py`.**
  - Repositorio `VoicePreferences`, con SQL parametrizado en constantes.
  - Rutas `GET` y `PUT /api/v1/voice/preferences`, autenticadas con la sesión de Clerk. Sin fila guardada, el modo es `off`.
  - El cuerpo rechaza campos extra, así que no se puede indicar otro usuario.
- **`main.py`.** Crea el repositorio junto a los demás de Turso y monta el router.
- **Frontend.**
  - `useAutoReadMode` lee la opción de la API al entrar y al cambiar de cuenta, y la guarda con `PUT`. Si falla, vuelve a la opción anterior y Perfil avisa.
  - Si no se puede leer, queda `off`, para no hablar por sorpresa.
  - Se retiró el guardado en `localStorage`, así que el modo elegido en la prueba local hay que volver a elegirlo una vez.

## Comprobaciones

- `unittest`: 31 pruebas correctas. Hay 2 nuevas en `tests/test_voice_preferences.py`, y en `test_turso` el recuento de migraciones pasa de 3 a 4 porque existe la 004.
- `python -m app.migrations --apply` sobre la base Turso configurada en `backend/.env` (la misma que usa producción) devolvió «Migraciones aplicadas». Después, la comprobación sin `--apply` devolvió «Esquema y migraciones verificados».
- Una API temporal en el puerto 8001 respondió `/health` con 200, y `GET`/`PUT /voice/preferences` sin sesión con 401.
- Frontend: `typecheck`, `lint`, `build` y Prettier sobre los archivos cambiados, todos correctos.

## Despliegue

Se eligió GitHub Actions en lugar de la CLI de Vercel: ejecuta las pruebas antes de publicar y es el flujo ya verificado en las entradas [10](10-fastapi-vercel-y-actions.md) y [frontend 03](../frontend/03-despliegue-vercel-y-cors.md). La migración se aplicó antes del push, para que la API nueva encontrara la tabla.

Resultado sobre `491a6e5`:

- Terminaron correctamente la [validación CI](https://github.com/benjamin12062006/copilot-voz/actions/runs/41180299936), el [despliegue del backend](https://github.com/benjamin12062006/copilot-voz/actions/runs/41180299960) y el [despliegue del frontend](https://github.com/benjamin12062006/copilot-voz/actions/runs/41180299921).
- En producción, `/health` responde 200 y `/api/v1/voice/preferences` sin sesión responde 401, así que la ruta existe y exige autenticación. El frontend responde (302 hacia el acceso).

Queda que el usuario elija el modo en Perfil, con su sesión en producción, y compruebe que se mantiene al recargar.
