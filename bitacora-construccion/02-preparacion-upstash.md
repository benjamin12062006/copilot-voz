# 02 — Preparación de Upstash y entorno Python

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Herramientas y entorno preparados; integración pendiente
Relacionada con: [fuentes Blob](../docs/fonts/09-upstash-blob-y-herramientas.md), [registro siguiente](03-base-web-y-orden-api-frontend.md)

## Trabajo realizado

El usuario sustituyó almacenamiento local por Blob privado. Se instaló marketplace upstash/skills y plugin upstash@upstash 1.2.7; entrada global nueva desactivada y habilitación limitada al proyecto. Las skills Blob-JS y CLI quedaron en `.agents/skills` del proyecto. No se autenticó OAuth ni se creó bucket.

Se preparó un servicio con uv, lock y dependencias FastAPI, uvicorn, pydantic-settings y upstash-blob. Su ubicación actual es [backend](../backend/01-preparacion.md). Las variables reales quedaron sin credenciales, ignoradas por Git; se añadieron exclusiones para entornos y artefactos.

`npx upstash --help` respondió. Una repetición en sandbox falló por DNS sin cambios remotos. Se verificaron resolución/imports del entorno; no escritura/lectura de objetos ni endpoints.

## Actualización de contexto

El servicio inicial se amplió en la planificación para identidad, usuarios, documentos, síntesis y entrada MCP. Las referencias del cliente anterior se retiraron por petición del usuario. Nuxt es ahora toda la interfaz y el reproductor. [API 03](../docs/plans/03-api-documentos-blob-y-markdown.md) conserva Blob como almacén de documentos; Turso se reserva a usuarios.

No hay conexión funcional a Blob todavía. Verificación remota y adaptador siguen pendientes; no se hicieron commits, tags ni despliegues.
