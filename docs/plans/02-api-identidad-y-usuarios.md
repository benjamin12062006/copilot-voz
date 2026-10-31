# 02 — API mínima de usuarios en Turso

Fecha de creación: 2026-10-30
Última actualización: 2026-10-31
Estado: Implementado y verificado localmente; migración remota pendiente
Relacionada con: [API 01](01-api-base-y-configuracion.md), [implementación](../../bitacora-construccion/backend/05-api-usuarios-turso.md), [fuentes](../fonts/17-api-minima-turso-y-token.md)

## Alcance vigente

Por instrucción del usuario: solo FastAPI, código sencillo y Clerk como emisor de token/ID. El frontend lo lleva otra IA. Se sustituye el enriquecimiento de perfiles del plan anterior: no consultar Clerk Backend User ni administrar cuentas. La base nueva debe ser exclusiva de Copilot.

| Método y ruta | Resultado implementado |
| --- | --- |
| GET /api/v1/auth/me | {identity:{subject,issuer}} del token verificado. |
| GET /api/v1/users/me | {user:{id,email,displayName,createdAt,updatedAt}} o 404. |
| PUT /api/v1/users/me | Crea o devuelve el mismo usuario; body vacío. |

La API verifica RS256, issuer exacto, fechas, sesión y origen. Usa JWKS público; no requiere CLERK_SECRET_KEY. Los orígenes usan CORS por defecto. Una lista personal de IDs configurada restringe acceso; sin lista se aceptan las sesiones válidas de la instancia. Email/nombre quedan null en esta etapa.

Turso conserva UUID local, issuer/subject únicos y fechas UTC. Una operación SQL atómica resuelve altas simultáneas sin cambiar los datos existentes. No hay Redis, documentos ni voz en este incremento.

## Ejecutar desde backend/

```bash
uv sync --locked
uv run --locked python -m app.database
uv run --locked python -m app.migrations --apply
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Solo dos credenciales de almacenamiento: TURSO_DATABASE_URL y TURSO_AUTH_TOKEN. CLERK_ISSUER es el origen público confiable para verificar tokens. No se migra durante el arranque. Sin configuración de proveedor la salud responde y las operaciones dependientes devuelven 503.

## Comprobado y pendiente

11 pruebas locales pasan: contratos HTTP, errores, SQL parametrizado, aislamiento, concurrencia y migraciones verificadas. SELECT 1 contra la URL configurada respondió correctamente. Esa URL corresponde a database-estadistica-forms, no a una base nueva identificada como Copilot. No se aplicó DDL remoto; la revisión automática rechazó inspeccionar el esquema por falta de autorización específica.

Pendientes: confirmar la base exclusiva, aplicar allí la migración y comprobar un token real. No se declara cierre remoto del plan.
