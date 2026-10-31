# 04 — VOZ y filosofía de lectura humana

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Investigación
Relacionada con: [arquitectura](../product/03-arquitectura-y-legibilidad.md), [voz/MCP](../plans/04-api-voz-y-mcp.md)

Tipo de fuente: skill local, documentación propia y originales de cursos. Consulta: 2026-10-30.

## F1 — Contrato previo de VOZ

Original: [voz-skill/SKILL.md](/Users/benji/.agents/skills/voz-skill/SKILL.md), apartados Estados y comandos, Flujo obligatorio y Formato de voz. La skill conserva activación por chat, lee respuestas recientes y escribe TXT secuenciales con retención de veinte archivos. Genera contenido para hablar; no implementa un sintetizador ni pausa real.

Adaptación al producto: documentos con ID, título, formato y propietario, guardados en Blob. Entrada manual/importación en Nuxt y entrada desde agentes por MCP. No copiar vigilancia de carpeta ni borrado automático de documentos. Pausa/continuar/inicio pertenecen al reproductor de Nuxt; el backend genera audio. Estudiar la skill como fuente no activa su modo de voz en este chat.

## F2 — Filosofía solicitada

Documentos propios consultados y referencias directas:

- [Plan de legibilidad](/Users/benji/Documents/KSuT/claudeLearningAllPosibolIt/docs/plans/feature/projects&catalog-import/05-plan-legibilidad-modulos.md).
- [Bitácora de legibilidad](/Users/benji/Documents/KSuT/claudeLearningAllPosibolIt/bitacora-construccion/feature/projects&catalog-import/04-legibilidad-modulos.md).
- [Criterios de legibilidad](/Users/benji/Documents/KSuT/claudeLearningAllPosibolIt/docs/fonts/feature/projects&catalog-import/07-legibilidad-modulos-clean-code.md).
- [Lectura humana de HTTP/types](/Users/benji/Documents/KSuT/claudeLearningAllPosibolIt/docs/fonts/types/02-legibilidad-common-http.md).

Evidencia: funciones principales con pasos expresivos; mantener relacionados los detalles; nombrar condiciones; comentar decisiones, no repetir sintaxis. Evitar capas y extracciones sin beneficio para quien leerá el código. Las comprobaciones descritas allí pertenecen a ese proyecto.

## F3 — Originales contrastados

Biblioteca: `/Users/benji/Documents/chrome-extencions/trancripciones/Arquitectura/Código Limpio`. Metadatos: curso Udemy `writing-clean-code`; las fichas históricas atribuyen instructor a Maximilian Schwarzmüller, sin revalidar aquí su identidad con otra fuente.

| Original y localizador | Principio conceptual aplicado |
| --- | --- |
| Sección 3 Code Structure, Comments & Formatting / 33. Vertical Formatting.md, líneas 13 y 21–31 | Flujo de arriba abajo y proximidad de conceptos relacionados. |
| Sección 4 Functions & Methods / 49. Why Levels of Abstraction Matter.md, líneas 19–27 | Acción principal con nivel de detalle coherente. |
| Sección 4 Functions & Methods / 54. Don't Overdo It - Avoid Useless Extractions.md, líneas 13–15 y 23–27 | Extraer solo si mejora comprensión. |

Estos pasajes conceptuales se consultaron como originales; no se reconstruyó código de esas clases. Propuesta propia: módulos pequeños por funcionalidad, un recorrido explicado por incremento y validación antes de ampliar alcance. [Arquitectura](../product/03-arquitectura-y-legibilidad.md).

## Organización documental

La referencia [HANDLE-BUSINESS/docs](/Users/benji/Documents/HANDLE-BUSINESS/docs) orienta la separación de producto, planes, fuentes y pocos diagramas. Aquí docs y bitácora son compartidos en la raíz, por petición del usuario; frontend y backend tienen directorios de código independientes.
