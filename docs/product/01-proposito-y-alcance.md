# 01 — Propósito y alcance

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [requisitos](02-requisitos-y-recorrido.md), [orden](../01-indice.md)

Copilot organiza documentos personales y permite escucharlos. El primer recorrido es entrar con Clerk, abrir Voz, crear o importar un documento `.md` o `.txt`, guardarlo en Blob, seleccionarlo y reproducirlo. Pausa continúa desde la misma posición; reiniciar vuelve al principio.

## Primer alcance

API autenticada con perfiles en Turso, documentos privados en Blob, preparación semántica de Markdown, síntesis de voz Python y herramientas MCP sobre los mismos casos de uso. Después, una interfaz Nuxt con Inicio y Voz, inspirada en la referencia Focus.

El navegador puede seleccionar archivos mediante una acción del usuario. El documento confirmado se recupera de Blob aunque el archivo original desaparezca. La biblioteca no depende de vigilar una carpeta del Mac. No se construye almacenamiento offline persistente.

No se incluyen aún generación automática de respuestas con IA, chats, sincronización de carpetas, colaboración, calendario, etiquetas, exportación PDF/DOCX ni lectura de todo el sistema de archivos. El límite de veinte TXT de la skill original no se convierte en borrados remotos automáticos.

## Estado

Existe la base Nuxt de acceso/cuenta y el entorno Python. La funcionalidad completa está planificada y pendiente. La calidad de una voz se decidirá escuchándola, con latencia y memoria medidas.
