# 09 — Upstash Blob y entorno Python

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Preparación parcial verificada
Relacionada con: [API 03](../plans/03-api-documentos-blob-y-markdown.md), [bitácora](../../bitacora-construccion/backend/02-preparacion-upstash.md)

Tipo de fuente: documentación oficial y herramientas instaladas. Consulta: 2026-10-30.

| ID | Fuente directa y sección | Evidencia aplicable |
| --- | --- | --- |
| U1 | [Python SDK](https://upstash.com/docs/blob/sdks/py/overview), Bucket/AsyncBucket | SDK oficial síncrono y async; elegir lifecycle y cierre adecuados. |
| U2 | [Connecting](https://upstash.com/docs/blob/bucket/connecting), token | Token de bucket en servidor; no distribuir a Nuxt ni agentes. |
| U3 | [Writing](https://upstash.com/docs/blob/bucket/writing), conditional writes | Verificar no-sobrescritura y condiciones ETag para conflictos por objeto. |
| U4 | [Reading](https://upstash.com/docs/blob/bucket/reading), list/info | Listado por prefijo y paginación, sin consultas de base de datos por título. |
| U5 | [Private documents](https://upstash.com/docs/blob/recipes/private-documents) | Lectura privada requiere autorización o enlace temporal limitado. |
| T1 | [upstash/skills](https://github.com/upstash/skills) | Marketplace/plugin y skills para agentes, independientes del SDK runtime. |
| T2 | [uv sync](https://docs.astral.sh/uv/concepts/projects/sync/) | Entorno aislado reproducible con lock. |

Decisión propia: documentos pequeños en un objeto JSON con original y metadata juntos. FastAPI autoriza y usa AsyncBucket; Nuxt solo llama nuestra API. No guardar documentos de usuario en Turso dentro de esta fase. Los costes del listado se medirán antes de sumar un índice.

## Instalación real

Plugin `upstash@upstash` 1.2.7 instalado en Codex, global nuevo desactivado y habilitado en la configuración de este proyecto. Skills [upstash-blob-js](../../.agents/skills/upstash-blob-js/SKILL.md) y [upstash-cli](../../.agents/skills/upstash-cli/SKILL.md) locales al proyecto, revisión upstream `adffa8896cd8e75649366a34183ecab6156e33c0`. No existe una skill Python específica entre las revisadas; sus APIs se toman de U1 y del SDK instalado.

El entorno de [backend](../../backend/01-preparacion.md) tiene upstash-blob resuelto por uv. `npx upstash --help` respondió; no se creó bucket ni se autenticó OAuth. Plugin instalado no significa almacén conectado. La configuración de Codex requiere proyecto de confianza y puede requerir recarga para detectar herramientas.
