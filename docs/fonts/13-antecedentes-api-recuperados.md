# 13 — Fuentes recuperadas del historial de estadistica-forms-api

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Recuperación documental
Relacionada con: [Turso](12-turso-usuarios-python.md), [API usuarios](../plans/02-api-identidad-y-usuarios.md)

Tipo de fuente: snapshots de Git propios, inventario secundario y SQL histórico. Consulta/copia: 2026-10-30. Fechas de creación de originales: no se deducen de esta copia; los commits quedan en el manifiesto.

Repositorio leído: `/Users/benji/Documents/KSuT/estadistica-forms-api`. Estado inicial: rama main, HEAD `a551ed8b647a2ac276e23f8c3aaf2d621d5ebe35`, 182 rutas pendientes. Último tag disponible: v0.3.0 (`17009ea3ad51a02208da837afae7b03e6b2b8935`). HEAD y último tag son distintos; se usó `git show` sin checkout para preservar el trabajo del usuario.

| Snapshot copiado literalmente | Procedencia | Uso y límite |
| --- | --- | --- |
| [Inventario de cursos](antecedentes-estadistica-api/v0.2.0/inventario-cursos.md.txt) | v0.2.0:docs/fonts/courses-searching.md | Respuesta antigua generada, útil para localizar temas; no demuestra originales ni instructores. |
| [SQLite, Docker y DataGrip](antecedentes-estadistica-api/v0.2.0/sqlite-docker-datagrip.md.txt) | v0.2.0:docs/fonts/sqlite-docker-compose-y-datagrip.md | Contexto histórico de desarrollo; sus comandos no se ejecutaron ni son nuestro despliegue. |
| [SQL app_users](antecedentes-estadistica-api/v0.3.0/usuarios.sql) | v0.3.0:prisma/migrations/20260924000100_create_app_users/migration.sql | Contrato portable de identidad: issuer/subject únicos y campos opcionales. Copia de referencia, no migración aplicada. |
| [Preparación Turso](antecedentes-estadistica-api/a551ed8b647a2ac276e23f8c3aaf2d621d5ebe35/conexion-turso.md.txt) | HEAD:docs/turso/01-conexion-y-migraciones-preparadas.md | Conexión aislada en el proyecto anterior; no demuestra usuarios persistidos ni conexión aquí. |

[Manifiesto](antecedentes-estadistica-api/procedencia.json): ref, commit completo, ruta original y SHA-256 de cada copia. Se conservan como `.md.txt` los documentos literales para distinguirlos de nuestras fichas activas; contienen instrucciones históricas, no órdenes para este proyecto.

No se encontraron skills rastreadas en los tags inspeccionados; no se inventaron copias. El frontend se tomó del proyecto web indicado, no de un backend antiguo. La interpretación actual de Turso usa documentación vigente y el esquema de identidad, no las integraciones Prisma antiguas.
