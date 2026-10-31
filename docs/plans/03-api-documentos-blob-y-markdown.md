# 03 — API: documentos Blob y preparación Markdown

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [Blob](../fonts/09-upstash-blob-y-herramientas.md), [Markdown](../fonts/08-markdown-pantalla-y-voz.md)

## Objetivo

Después de usuarios autenticados, guardar documentos privados y obtener una representación coherente para pantalla y voz. El servidor prepara el contenido; Nuxt dibujará los bloques. [Modelo de datos](../product/04-datos-y-formatos.md).

## Incrementos y contratos propuestos

1. Definir `Document`, resumen y documento preparado. Guardar un objeto JSON por documento en Blob con metadata y original juntos; ruta generada a partir del ID local del usuario autenticado. No usar Turso para documentos en este alcance.
2. Implementar crear/listar/leer/actualizar con AsyncBucket, lifecycle, páginas pequeñas y condición de escritura. Exponer `revision` opaca a partir de ETag; verificar los parámetros reales del SDK antes de programar conflictos.
3. Importar `.txt`, `.md`, `.markdown`: UTF-8 estricto, BOM opcional, validación de tamaño máximo y título. Validar bytes recibidos antes de asignar el formato; no confiar solo en Content-Type o extensión. La UI futura leerá archivo y enviará texto; no hace falta multipart en el primer recorrido. Formato desconocido se rechaza o se ofrece como texto por decisión explícita.
4. Añadir `markdown-it-py` y verificar sus tokens, preset CommonMark y extensión de tablas. Definir DTO propio de bloques; no exponer tipos del parser por la API. Soporte de tareas mediante plugin compatible solo si se valida; no prometer GFM completo. HTML desactivado, sin renderizado ejecutable ni solicitudes a destinos contenidos en el texto.
5. Producir `blocks`, `spokenText`, `warnings`, `preparationVersion`, `documentId` y `revision` en una sola interpretación. Texto plano no pasa por el parser Markdown.

| Método y ruta | Resultado propuesto |
| --- | --- |
| `POST /api/v1/documents` | Body `{title,format,original}`; 201 `{document}`. |
| `GET /api/v1/documents?cursor=...` | `{items:[resumen],nextCursor}` con límite de página y cursor validado. |
| `GET /api/v1/documents/{id}` | `{document}` original, formato, fechas y revision. |
| `PUT /api/v1/documents/{id}` | Body con título, formato, original y revision requerida; `{document}` o 409. |
| `GET /api/v1/documents/{id}/prepared` | `{prepared}` con bloques, texto hablado y avisos. |

Aplazar borrar/exportar hasta necesitarlos; nunca añadir retención automática destructiva. Un recurso ajeno responde 404. No devolver el token ni permitir rutas arbitrarias del bucket.

La entrada MCP del paso 04 necesita idempotencia durable del guardado: asociar la clave al propietario, derivar un ID estable de documento y usar creación sin sobrescritura; ante repetición comprobar fingerprint del contenido. Una clave repetida con otro contenido es conflicto. Definir longitud/caducidad de claves y verificar recuperación tras reiniciar el proceso antes de prometer esta garantía. No guardar un índice adicional de documentos en Turso.

## Política de lectura

| Contenido | Pantalla Nuxt futura | Voz preparada por Python |
| --- | --- | --- |
| Texto plano | Literal, preservando saltos. | Literal, incluyendo C#, a*b y #etiqueta. |
| Títulos, énfasis, párrafos | Jerarquía de bloques y estilos. | Palabras en orden, pausas por bloque, sin marcas. |
| Enlaces | Texto y destino explícito al abrirlo voluntariamente. | Etiqueta, sin URL larga por defecto. |
| Listas y citas | Estructura e indentación. | Elementos y orden, sin leer viñetas como signos. |
| Tablas | Filas/cabeceras accesibles. | Cabecera y valor por celda; avisar si no se puede preservar asociación. |
| Código y Mermaid | Bloque literal; Original siempre disponible. | Omitir por defecto con aviso; opción futura de lectura literal. |
| Imágenes | Texto alternativo y aviso sin descarga automática. | Alt si existe; no inventar descripción. |
| HTML/MDX | Literal/aviso según política; sin ejecución. | Omitir con aviso; MDX no soportado como programa. |
| Sintaxis no reconocida | Acceso a Original y degradación legible. | No inventar estructura; avisar de pérdida. |

## Cierre previsto

Guardar/recuperar exactitud del texto, CRLF/BOM, acentos, UTF-8 inválido, vacío, tamaño excesivo y conflictos. Probar separación entre dos propietarios con repositorio controlado aunque producción sea personal. Verificar paginación, fallos Blob y original disponible al fallar preparación. Usar ejemplos pequeños con salida esperada de listas/enlaces/tablas/código; no regex para borrar símbolos Markdown. Tras confirmación remota, quitar el archivo importado no debe impedir recuperar su contenido.

Actualizar contratos con resultados del parser; continuar con [API 04](04-api-voz-y-mcp.md).
