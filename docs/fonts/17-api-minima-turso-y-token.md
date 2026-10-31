# 17 — Token verificado y usuarios en Turso

Fecha de creación: 2026-10-31
Tipo de fuente: documentación oficial, paquetes instalados y código propio
Fecha de consulta: 2026-10-31
Relacionada con: [plan 02](../plans/02-api-identidad-y-usuarios.md), [implementación](../../bitacora-construccion/backend/05-api-usuarios-turso.md), [SQL histórico](13-antecedentes-api-recuperados.md)

| ID | Localización | Evidencia y aplicación |
| --- | --- | --- |
| F1 | [Turso Python Quickstart](https://docs.turso.tech/sdk/python/quickstart), Remote libSQL database | Conexión remota con libsql.connect y auth_token. Driver instalado: libsql 0.1.11; no se instaló un segundo driver. |
| F2 | [Clerk: Manual JWT verification](https://clerk.com/docs/guides/sessions/manual-jwt-verification), public key / verify signature | Verificar token con clave pública sin administrar usuarios. Adaptación: JWKS del issuer confiable, sin consultar Backend User. |
| F3 | [PyJWT API](https://pyjwt.readthedocs.io/en/stable/api.html), jwt.decode / PyJWKClient | Algoritmo fijado en servidor, issuer y claims requeridos. Adaptación: RS256, fechas, sub/sid, origen y sesión activa. Versión instalada: 2.15.1. |
| F4 | [SQLite UPSERT](https://sqlite.org/lang_upsert.html), Description; [RETURNING](https://sqlite.org/lang_returning.html), Processing Order | Restricción única elige la fila existente; RETURNING devuelve la escritura. Adaptación: una operación atómica que conserva ID y fechas y consume el resultado antes del cierre. |
| F5 | [SQL recuperado](antecedentes-estadistica-api/v0.3.0/usuarios.sql) | Contrato issuer/subject únicos. Adaptación a SQLite y fechas UTC, sin atribuirlo a un curso de Clerk/Turso. |

La documentación no demuestra conexión ni migración. SELECT 1 fue remoto; rutas, migraciones y concurrencia se probaron con libSQL temporal y firmas sintéticas. Los cursos FastAPI consultados aportan contexto general de dependencias; no se les atribuye esta integración de proveedores.
