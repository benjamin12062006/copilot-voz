# 04 — Datos, propiedad y formatos

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [Turso](../fonts/12-turso-usuarios-python.md), [Blob](../fonts/09-upstash-blob-y-herramientas.md), [Markdown](../fonts/08-markdown-pantalla-y-voz.md)

## Usuarios: Turso

`app_users`: UUID local en `id`, `identity_issuer`, `identity_subject`, `email` nullable, `display_name` nullable, fechas UTC ISO-8601. Restricción única `(identity_issuer, identity_subject)`. El sujeto de Clerk no sustituye al ID local. Aprovisionar repetidamente no crea duplicados ni altera `created_at`. [SQL histórico recuperado](../fonts/13-antecedentes-api-recuperados.md).

Clerk es autoridad de identidad; email y nombre son una proyección opcional. El JWT de sesión no garantiza email. Resolver el usuario con Backend API cuando falten datos, con actualización controlada. No almacenar contraseñas, JWT ni token de sesión en Turso.

## Documentos: Blob privado

Blob es el almacén canónico de documentos; Turso se reserva a usuarios en este alcance. Propuesta: un objeto JSON UTF-8 por documento con `schemaVersion`, `id`, `ownerId`, `title`, `format` (`plainText`/`markdown`), `original`, `createdAt`, `updatedAt`. Original es una cadena íntegra, no HTML ni una versión corregida por el lector. El contenedor JSON interno no cambia los formatos `.md` y `.txt` que usa el usuario.

Ruta calculada por la API: `copilot/dev/users/{localUserId}/documents/{uuid}.json`. La API no acepta una clave Blob arbitraria. Aislar por prefijo y comprobar propiedad también al recuperar; no exponer tokens del bucket. Listar páginas pequeñas, obteniendo cada resumen con lecturas acotadas: Blob no ofrece consultas de base de datos. Medir este coste antes de introducir un índice nuevo.

Crear exige no sobrescribir; actualizar usa la condición ETag documentada por el SDK, verificada al implementar. El ETag es opaco y la API lo presenta como `revision`. No reconstruirlo con una fecha. Un conflicto conserva el borrador y devuelve 409; no pisa silenciosamente otro cambio. No hay transacción Turso–Blob porque el documento y su metadata se escriben juntos.

## Lectura

Texto plano conserva signos literales. Markdown se interpreta en Python a bloques estructurados, texto hablado y avisos. El frontend dibuja esos bloques con componentes Vue; no inserta HTML remoto con `v-html`. No se ejecuta HTML, código ni Mermaid; no se descargan imágenes ni URLs incrustadas. [Política detallada](../plans/03-api-documentos-blob-y-markdown.md).

Admitir `.md`, `.markdown` y `.txt`, con límite inicial propuesto 1 MiB y UTF-8 estricto, BOM opcional y CRLF normalizado solo para preparar. Conservar original importado como texto; no prometer fidelidad binaria de codificaciones ajenas. PDF, DOCX, RTF y MDX no forman parte del primer lector.

## Audio

Audio derivado de una revisión del documento y opciones de voz; nunca sustituye al original. Empezar con un artefacto temporal del backend, ID opaco, propietario y caducidad, con entrega autenticada. Limpiar solo audio temporal propio. Persistir audio en Blob y reutilizarlo por hash queda para cuando las mediciones lo justifiquen. La UI mantiene un Object URL revocable para su sesión; no lo confunde con un enlace privado durable.
