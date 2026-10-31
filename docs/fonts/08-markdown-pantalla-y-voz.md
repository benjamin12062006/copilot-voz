# 08 — Markdown para pantalla y voz

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Investigación; parser propuesto
Relacionada con: [formatos](../product/04-datos-y-formatos.md), [API 03](../plans/03-api-documentos-blob-y-markdown.md)

Tipo de fuente: documentación oficial de parser y propuesta de contrato. Consulta: 2026-10-30.

F1 — [markdown-it-py: Using markdown_it](https://markdown-it-py.readthedocs.io/en/latest/using.html), Tokens / presets: primero interpreta tokens y después puede producir representaciones. CommonMark y reglas de tablas son configurables; no asumir soporte universal de extensiones.

F2 — [Security](https://markdown-it-py.readthedocs.io/en/latest/security.html): las opciones y extensiones afectan el tratamiento de contenido no confiable. Desactivar HTML y no insertar HTML crudo en la UI forma parte de nuestra política.

Interpretación: un parser estructural permite preparar voz sin eliminar signos con regex. Adaptación propia: un único módulo Python produce bloques visuales serializables, texto hablado y avisos. Vue dibuja esos bloques y ofrece Original. El DTO y las reglas de lectura son nuestros; el parser no sintetiza voz ni decide cómo leer tablas.

El paquete aún no está instalado ni evaluado con nuestros ejemplos. Antes de fijarlo, verificar tokens de tablas, enlaces, imágenes, listas y código, así como compatibilidad de plugins. No prometer GFM/MDX completo. Las reglas y casos de aceptación están en [API 03](../plans/03-api-documentos-blob-y-markdown.md).
