# 01 — API FastAPI

Fecha de creación: 2026-10-30
Última actualización: 2026-10-31
Estado: API mínima implementada; migración remota pendiente
Relacionada con: [plan 02](../docs/plans/02-api-identidad-y-usuarios.md), [bitácora backend](../bitacora-construccion/backend/05-api-usuarios-turso.md)

## Ejecutar desde backend/

```bash
uv sync --locked
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

GET /health comprueba el proceso. GET /api/v1/auth/me verifica el token recibido; GET/PUT /api/v1/users/me leen o crean el perfil. Email/nombre son null en esta etapa; no se consulta Clerk Backend API ni se necesita su secret key.

## Configuración mínima

TURSO_DATABASE_URL y TURSO_AUTH_TOKEN conectan la base libSQL remota. CLERK_ISSUER es el origen público confiable del emisor del token; desde ahí se consulta su JWKS público. Las variables existentes de public key, orígenes específicos e IDs permitidos son opcionales. Las credenciales reales permanecen en .env ignorado por Git.

```bash
uv run --locked python -m app.database
uv run --locked python -m app.migrations
uv run --locked python -m app.migrations --apply
```

El primer comando ejecuta SELECT 1; el segundo comprueba esquema sin escribir; --apply aplica la migración manual, transaccional y registrada. El servidor nunca migra al arrancar. Usar una base exclusiva de Copilot.

## Verificación

```bash
uv run --locked python -m unittest discover -s tests -q
```

11 pruebas locales pasan con libSQL temporal y firmas RSA. La conexión remota SELECT 1 fue correcta, pero la URL actual identifica database-estadistica-forms; su inspección fue rechazada por revisión automática. No se aplicó DDL remoto. Falta confirmar la base exclusiva y probar una sesión real; issuer todavía no configurado.

Parser, documentos, voz y MCP pertenecen a planes posteriores. El frontend lo lleva otra IA.

## Tokens MCP personales

Actualización 2026-10-31: el backend ya emite tokens por usuario con sesión Clerk (POST /api/v1/mcp/tokens), lista metadata y permite revocarlos. Se retiró la configuración global de propietario/token. La migración 002 agrega app_mcp_tokens a Turso; el runner aplica 001→002 sin alterar usuarios existentes. El contrato del botón está en [bitácora 07](../bitacora-construccion/backend/07-tokens-personales-y-textos-por-usuario.md). Los originales nuevos se guardan en textos/userId/fileId.md o .txt, con limpieza de versiones retiradas. No se ejecutó la migración en Turso remoto.
