# 05 — API mínima de usuarios y Turso

Fecha de creación: 2026-10-30
Última actualización: 2026-10-31
Estado: Implementado y verificado localmente; migración remota pendiente
Ámbito: backend FastAPI
Relacionada con: [API 02](../../docs/plans/02-api-identidad-y-usuarios.md), [API base](04-api-base-y-configuracion.md), [fuentes](../../docs/fonts/17-api-minima-turso-y-token.md)
Revisión de partida: 663e454

## Necesidad y decisión

Ejecutar API 02 con código legible y una base nueva exclusiva de Copilot. El usuario encargó frontend a otra IA y precisó que Clerk solo proporciona token/ID. Se implementan tres rutas, sin consultar perfiles de Clerk ni administrar cuentas. No se implementan Redis, documentos ni voz.

La verificación sigue [Clerk: JWT con clave pública](https://clerk.com/docs/guides/sessions/manual-jwt-verification): no requiere secret key ni Backend User. Email/nombre son null. Por decisión de alcance, una lista de IDs solo restringe si está configurada; en otro caso se aceptan sesiones de la instancia confiable. Esto sustituye el enriquecimiento y allowlist obligatoria del plan anterior.

## Responsabilidades y legibilidad

| Archivo y símbolo | Función |
| --- | --- |
| [api.py](../../backend/app/api.py), read_identity/read_user/provision_user | Rutas pequeñas: identidad verificada → repositorio → respuesta. El body no decide identidad. |
| [auth.py](../../backend/app/auth.py), SessionAuthenticator.verify | Firma, fechas, emisor, origen y sesión; condiciones nombradas, detalle criptográfico separado. |
| [database.py](../../backend/app/database.py), SqlUserRepository | SQL parametrizado y conexión por operación; errores sanitizados. |
| [users.py](../../backend/app/users.py) | Datos con nombres, alias camelCase y fechas UTC. |
| [SQL](../../backend/migrations/001_app_users.sql) y [runner](../../backend/app/migrations.py) | Migración manual transaccional, checksum y verificación de esquema; rechazo de tablas ajenas. |
| [main.py](../../backend/app/main.py), create_app/lifespan | Composición y rutas; conserva salud, errores, CORS y request ID. No ejecuta DDL al arrancar. |

El [UPSERT](https://sqlite.org/lang_upsert.html) con [RETURNING](https://sqlite.org/lang_returning.html) devuelve la fila ganadora en una operación atómica, conservando perfil, UUID y fechas. La prueba concurrente detectó contención al usar dos statements bajo una transacción larga; la operación única la resolvió. La unicidad protege también entre procesos.

Se instaló libsql 0.1.11 para el motor Cloud predeterminado según [Turso Python](https://docs.turso.tech/sdk/python/quickstart). Compiló desde fuente en Python 3.14/macOS. PyJWT con crypto verifica tokens; no queda clerk-backend-api como dependencia.

## Comprobaciones

- uv sync --locked --offline y compileall: correctos.
- Servidor real uvicorn en 127.0.0.1:18062: GET /health 200, arranque y cierre completos. Se detuvo solo el proceso creado para comprobarlo.
- [11 pruebas](../../backend/tests/test_turso.py): migración repetible/checksum, esquema alterado, tablas ajenas, nulos, aliases/fechas, aislamiento, SQL parametrizado, dos altas simultáneas con mismo ID, errores y recorrido HTTP con JWT RSA sintético.
- HTTP controlado: identidad 200; sesión ausente/inválida/expirada o issuer/origen ajeno 401; ID fuera de lista configurada 403; perfil ausente 404; PUT repetido y GET 200; proveedor ausente 503.
- Turso remoto: SELECT 1 correcto. El sandbox impedía cargar el llavero de certificados; el mismo comando con acceso permitido a red/certificados funcionó.
- La URL real apunta a database-estadistica-forms. No se migró ni se inspeccionó el esquema: la revisión automática rechazó esa inspección porque se había autorizado una base nueva exclusiva. Falta resolver el destino antes de escribir.

No se ha probado una sesión real: falta el issuer confiable en la configuración actual. Las pruebas usan una base temporal que se elimina al finalizar; no sustituyen validación remota.

## Organización

Bitácora separada en backend/ y frontend/, conservando fechas, números históricos y enlaces. La parte de interfaz de la antigua entrada 03 pasó a frontend/01. No se editaron archivos de frontend/.

Se copiaron completas las skills [Turso](../../.agents/skills/turso/SKILL.md) (1 archivo) y [Upstash Redis](../../.agents/skills/upstash-redis-js/SKILL.md) (32 archivos), verificadas byte a byte. Estarán disponibles en el próximo turno. Redis no interviene en esta API.
