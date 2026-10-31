# 18 — Blob condicional y MCP Python

Fecha de creación: 2026-10-31
Tipo de fuente: documentación oficial, SDK instalado y contratos del proyecto
Relacionada con: [bitácora](../../bitacora-construccion/backend/06-biblioteca-blob-y-envio-mcp.md)

- [Upstash Python SDK](https://upstash.com/docs/blob/sdks/py/overview): AsyncBucket con ciclo de vida async. SDK local 0.1.0: get devuelve content y etag; put acepta allow_overwrite e if_unchanged. Se verificaron firmas con inspect y escritura real.
- [Upstash Writing](https://upstash.com/docs/blob/bucket/writing), conditional writes: creación sin sobrescribir y actualización condicionada por ETag. Adaptación propia: biblioteca acotada por usuario, retención y guardado atómicos; conflicto reintenta con la versión actual. No es una receta copiada de un curso.
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk): versión instalada 2.3.0, MCPServer (FastMCP fue renombrado en v2). Handshake y tools/list por stdio ejecutados.
- [Contrato frontend](../../frontend/app/types/documents.ts): content, markdown/text, revision numérica, bloques y notices. Se leyó código; no se modificó ni conectó frontend.
- [voz-skill](/Users/benji/.agents/skills/voz-skill/SKILL.md): referencia funcional de máximo 20 y retención por antigüedad. Adaptación explícita: documentos remotos por propietario, sin usar el directorio de voz local como almacén del producto.

Consulta: 2026-10-31. La idempotencia de esta implementación dura mientras el documento siga retenido; no se promete un historial infinito de claves después de retirar documentos.
