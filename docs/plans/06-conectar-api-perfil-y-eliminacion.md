# 06 — Conexión real, tokens en Perfil y eliminación

Fecha de creación: 2026-10-31
Estado: Implementado y verificado (CORS, migraciones, pruebas y build; listo para uso en navegador)
Relacionada con: [tokens](02.1-tokens-mcp-por-usuario.md), [Blob](03-api-documentos-blob-y-markdown.md), [frontend](05-frontend-acceso-y-panel-voz.md), [bitácora backend 08](../../bitacora-construccion/backend/08-retencion-borrado-y-migracion-turso.md), [bitácora frontend 02](../../bitacora-construccion/frontend/02-conexion-api-perfil-mcp-y-voz-en-vivo.md)

## Objetivo autorizado

Aplicar migraciones en Turso configurado, conectar perfiles y documentos del frontend con FastAPI, generar/copiar/revocar tokens personales desde Perfil y borrar documentos solo desde web. La última corrección del usuario deja la retención automática configurable solo en web y aplicada por API; el MCP no la configura.

## Secuencia

1. Inspeccionar esquema remoto sin leer filas de usuarios; aplicar únicamente migraciones de Copilot si el destino y el esquema permiten hacerlo sin alterar recursos ajenos.
2. Persistir la preferencia de retención por usuario en la biblioteca Blob (20 por defecto; rango acotado). Reducir el límite requiere confirmación web porque retira originales antiguos. Añadir borrado con revisión esperada, aislado por propietario, sin herramienta MCP de borrado.
3. Cliente HTTP único con Bearer Clerk y un reintento de sesión; servicios de documentos/tokens/preferencias. Conectar datos reales por defecto manteniendo vista previa explícita y voz local existente.
4. Perfil: bloque «Acceso MCP» para emitir/copiar/revocar token, y bloque «Almacenamiento» para límite automático. Documento: eliminación explícita con confirmación.
5. Comprobar migraciones, autenticación/propiedad, retención y borrado; typecheck/lint/build de Nuxt, pruebas backend y validación de interfaz si hay sesión disponible.

## Límites

No implementar síntesis Python: la voz del sistema ya funciona en frontend y se conserva. No mostrar secretos en logs/documentación. Los tokens nuevos solo se muestran una vez y no se guardan en localStorage. Conexión Clerk requiere issuer confiable, que puede derivarse de la clave publicable ya configurada en frontend, sin copiar su secret key.

Corrección expresa del usuario: ninguna eliminación manual ni cambio de límite desde MCP. Ambas operaciones corresponden exclusivamente a web/Perfil. MCP conserva solo envío de Markdown.
