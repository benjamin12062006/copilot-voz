---
name: construir-con-evidencia
description: "Construir funcionalidades fundamentadas en cursos y conservar documentación histórica del proyecto: bitácora, fuentes y planes Markdown fechados, relacionados y numerados por carpeta. Usar al implementar o modificar funcionalidades relevantes desde cursos, preparar planes persistentes, registrar fuentes, pedir trazabilidad de decisiones o reconstruir el contexto de un cambio anterior. No crear entradas por formato, sintaxis o consultas sin implementación salvo petición expresa."
---

# Construir con evidencia

Unir investigación, planes, decisiones, implementación y verificación en un archivo documental que permita explicar por qué el código terminó así y qué contexto existía en una fecha concreta. La evidencia persistente pertenece al proyecto; esta skill conserva únicamente el procedimiento reutilizable.

## Coordinar las skills existentes

Leer y aplicar las dependencias pertinentes, sin duplicar sus buscadores ni perder la procedencia de las reconstrucciones:

- [$buscar-aprendizaje-en-cursos](../buscar-aprendizaje-en-cursos/SKILL.md): localizar originales y verificar pasajes con su script. Los resultados de búsqueda y las guías generadas no sustituyen a la transcripción.
- [$construir-desde-cursos](../construir-desde-cursos/SKILL.md): analizar las fuentes, adaptar sus mecanismos y resolver el objetivo del proyecto. Esta es la ruta habitual para construir.
- [$filosofia-de-trabajo](../filosofia-de-trabajo/SKILL.md): desarrollar incrementos comprensibles y comprobarlos antes de ampliar el alcance.
- [$aprender-desde-cursos](../aprender-desde-cursos/SKILL.md): usar su flujo docente cuando el usuario pida estudiar una clase en orden.
- [$reconstruir-codigo-curso](../reconstruir-codigo-curso/SKILL.md): reconstruir todas las lecciones pertinentes que `construir-desde-cursos` seleccione para comprender código, comparar mecanismos o aportar citas precisas. Cada guía es evidencia derivada y no sustituye al original.

Resolver los enlaces desde esta carpeta. Si falta una dependencia, buscar su nombre en los directorios de skills que exponga el entorno, incluyendo `~/.agents/skills`, `~/.codex/skills` y `$CODEX_HOME/skills` cuando corresponda. Leer el `SKILL.md` encontrado antes de seguirlo; ejecutar sus scripts mediante la ruta resuelta. No inventar una API de invocación ni guardar rutas de un equipo dentro de esta skill. Informar de dependencias ausentes y continuar con fuentes accesibles cuando permitan una solución fundada.

Los nombres informales «buscar-desde-cursos» y «filosofia-de-creacion» se corresponden aquí con las skills reales `buscar-aprendizaje-en-cursos` y `filosofia-de-trabajo`.

Esta skill añade una salida persistente a la consulta aplicada: fichas de fuentes, planes o una entrada de bitácora según corresponda. La reconstrucción se decide mediante `construir-desde-cursos`; el estudio sin implementación sigue su propio recorrido.

## 1. Recuperar contexto y determinar el alcance

En cada proyecto o chat nuevo, identificar la raíz de la aplicación objetivo, leer `AGENTS.md`, requisitos, decisiones vigentes y los archivos relevantes. Si hay Git, inspeccionar estado y diffs pertinentes; si no lo hay, continuar con el árbol real sin inventar revisiones. En un workspace con frontend y backend separados, elegir la raíz del componente modificado, salvo que ya exista una bitácora compartida.

Crear una entrada por incremento funcional coherente: una funcionalidad nueva, cambio de contrato, integración, decisión arquitectónica aplicada o corrección sustancial de comportamiento. Importa el efecto, no la cantidad de líneas: corregir una autorización puede necesitar evidencia aunque sea un cambio pequeño. No producir una entrada por archivo editado, comando ejecutado, ajuste de formato, typo o arreglo sintáctico sin cambio de comportamiento.

Para una pregunta, exploración o plan sin implementación, responder en el alcance solicitado. Guardar un plan o investigación solo si se pidió documentarlo, identificándolo como tal y sin afirmar que existe código implementado. Si se pide documentar retrospectivamente, distinguir las razones verificables de las inferencias; no atribuir investigación histórica que no consta.

## 2. Inicializar y descubrir el archivo documental

Inspeccionar el árbol antes de crear directorios. En el primer uso de la skill sobre una raíz de aplicación, asegurar esta estructura mínima, salvo que el usuario haya indicado otra ubicación equivalente:

```text
raíz-del-componente/
├── bitacora-construccion/
└── docs/
    ├── fonts/
    └── plans/
```

Usar `scripts/inicializar_documentacion.py` para crear únicamente los directorios ausentes. `bitacora-construccion/` conserva los incrementos implementados; `docs/fonts/` conserva fichas específicas de transcripciones, documentación oficial, páginas de Internet u otras fuentes consultadas; `docs/plans/` conserva planes de auth, features, arquitectura u otros temas antes de implementarlos. Se permiten subcarpetas temáticas en cualquiera de ellos cuando eviten mezclar contextos, por ejemplo `docs/plans/auth/` o `docs/fonts/descope/`.

`fonts` es el nombre convencional solicitado para este archivo de fuentes. No corregirlo a `sources` ni confundirlo con recursos tipográficos.

Reutilizar ubicaciones existentes por su contenido. La bitácora puede llamarse `fontsVersionBuilding`, `bitacora-construccion` o estar organizada de otra forma, incluso dentro de `docs/`. No mover ni duplicar documentación existente para imponer la estructura predeterminada. Si falta una de las tres áreas, crear solo la equivalente ausente. En un workspace con frontend y backend separados, inicializar la raíz del componente modificado salvo que exista un archivo compartido deliberado.

Los demás subdirectorios de `docs/`, como `autenticacion-descope/`, pueden contener contratos, respuestas sanitizadas, decisiones de proveedor o notas temáticas que no sean una ficha de fuente ni un plan. Descubrirlos y relacionarlos cuando aporten contexto; no meter todo Markdown dentro de `fonts/` o `plans/`.

Comando predeterminado:

```bash
python3 /ruta/resuelta/construir-con-evidencia/scripts/inicializar_documentacion.py /ruta/proyecto
```

## 3. Numerar, fechar y relacionar Markdown

Aplicar estas reglas a **todo Markdown que cree esta skill** en `bitacora-construccion/`, `docs/fonts/`, `docs/plans/` u otro subdirectorio documental del proyecto:

- Incluir cerca del título `Fecha de creación: AAAA-MM-DD`, usando la fecha local efectiva del entorno. No usar solo la fecha del chat si el entorno declara otra zona horaria.
- Conservar siempre la fecha de creación original. En una modificación sustantiva posterior, añadir o actualizar `Última actualización: AAAA-MM-DD` sin reemplazar la fecha original.
- Registrar `Relacionada con:` mediante enlaces relativos cuando existan antecedentes, fuentes, planes o entradas de implementación pertinentes.
- Registrar la revisión Git de partida o relacionada cuando exista y ayude a recuperar el estado del código. La fecha ordena el contexto, pero no sustituye al historial Git ni demuestra por sí sola qué código existía.
- Si un Markdown histórico carece de fecha, recuperar la primera revisión con `git log --follow` cuando sea posible. Si no hay evidencia suficiente, escribir `Fecha de creación: desconocida`; nunca atribuirle la fecha actual como si fuera histórica.

Numerar los Markdown nuevos por carpeta temática directa. Ordenar por prefijo numérico, usar `máximo + 1`, nunca el número de archivos; no rellenar huecos ni contar recursivamente otras carpetas. Empezar en `01` cuando esa carpeta no tenga entradas numeradas. Conservar el ancho y separador existentes; por defecto, `01-validar-sesion.md`, `02-crear-perfil.md`. Admitir prefijos subordinados como `03.1-...` cuando el documento amplíe específicamente el `03`; esos prefijos no consumen el siguiente número principal, que sería `04`. Los archivos anteriores sin número se conservan y no se renumeran automáticamente.

Ejemplo de secuencias independientes:

```text
bitacora-construccion/
├── auth/
│   ├── 01-validar-sesion.md
│   └── 02-crear-perfil.md
└── formularios/
    └── 01-publicar-formulario.md
docs/
├── fonts/
│   ├── 01-curso-guards-nest.md
│   └── 02-documentacion-descope.md
└── plans/
    └── auth/
        ├── 01-plan-autenticacion.md
        ├── 02-integrar-sesion-web.md
        └── 02.1-detallar-renovacion.md
```

Para inventariar la ubicación resuelta, usar el ayudante de solo lectura:

```bash
python3 /ruta/resuelta/construir-con-evidencia/scripts/inventariar_bitacora.py /ruta/proyecto/bitacora-construccion --carpeta auth
python3 /ruta/resuelta/construir-con-evidencia/scripts/inventariar_bitacora.py /ruta/proyecto/docs/plans --carpeta auth
```

El ayudante acepta como raíz una bitácora o cualquier carpeta documental. Su JSON informa de secuencias, números duplicados y el siguiente prefijo. No crea archivos ni reserva números. Leer los documentos pertinentes después de inventariar; el script no interpreta su contenido. Si detecta convenciones ambiguas o colisiones, examinarlas antes de elegir nombre. Volver a comprobar disponibilidad inmediatamente antes de escribir.

## 4. Investigar y contrastar antes de decidir

Seguir `construir-desde-cursos` y `buscar-aprendizaje-en-cursos` para localizar el conjunto suficiente de originales y reconstrucciones que respalde la implementación. Respetar la fuente principal elegida por el usuario. Identificar instructor, curso, sección y lección desde sus metadatos; no deducirlos a partir de una etiqueta ambigua.

Comparar varios cursos cuando aporten enfoques alternativos relevantes, resuelvan contradicciones o aumenten la certeza de una decisión. Una fuente suficiente es válida. Comparar el mismo problema bajo sus supuestos: versión, lenguaje, framework, persistencia, escala, responsabilidad y errores que contempla. Explicar qué se elige, combina o descarta, y con qué coste; no mezclar contratos incompatibles ni declarar una solución «mejor» sin criterio concreto.

Complementar vacíos y verificar APIs vigentes con documentación oficial cuando lo requieran la tarea o las instrucciones del entorno. Distinguir evidencia del curso, documentación oficial, restricciones del proyecto e inferencia propia. Si la biblioteca no cubre un proveedor, declararlo; por ejemplo, un curso de registro con contraseña puede aportar organización de módulos sin enseñar la integración con un proveedor de identidad externo.

Antes de implementar, conservar una relación compacta:

```text
Necesidad → original y pasaje → reconstrucción y símbolo → interpretación → alternativa → decisión propuesta
```

Usar esa relación en la entrada y actualizarla según el código real. Reconstruir tantas lecciones pertinentes como ayuden a recuperar el mecanismo; no inventar código ni utilizar una reconstrucción para rellenar evidencia ausente del original.

Cuando una fuente merezca contexto reutilizable más allá de una cita, crear una ficha desde `assets/fuente.md` en `docs/fonts/`. Cuando el trabajo necesite una ruta de implementación persistente, crear un plan desde `assets/plan.md` en `docs/plans/`. Un plan no afirma que el código existe; una ficha de fuente no sustituye al original.

## 5. Citar de forma verificable

Asignar identificadores locales como `F1`, `F2` a las fuentes realmente consultadas y enlazarlos junto a la afirmación que respaldan, mediante notas al pie o referencias Markdown. Una lista de enlaces al final sin relación con las decisiones no basta.

Asignar identificadores `R1`, `R2` a las reconstrucciones utilizadas. Para una decisión basada en código de curso, citar conjuntamente el original (`F…`) y la fase, símbolo o bloque final de la guía (`R…`). La cadena recomendada y genérica es:

```text
original y pasaje → reconstrucción y símbolo → principio transferible
→ adaptación al proyecto activo → archivo y símbolo implementado → comprobación realmente ejecutada
```

Omitir los eslabones que todavía no existan sin afirmar que están completos.

Para cada transcripción, registrar título, instructor si consta, curso, sección, nombre de archivo, ruta existente y un localizador recuperable: encabezado, timestamp disponible o líneas leídas. Añadir una frase de búsqueda breve cuando el texto tenga párrafos largos. Verificar las líneas con `nl -ba`/`rg -n`; no inventar timestamps ni usar fragmentos `#L…` que el visor no soporte.

Incluir citas textuales breves cuando la formulación exacta respalde una decisión o permita comprobar una interpretación. Copiar literalmente el pasaje consultado; dejar correcciones de transcripción y paráfrasis fuera de la cita, etiquetadas. No convertir un resumen generado en palabras del instructor. Respetar límites de reproducción aplicables y evitar copiar lecciones completas.

Para fuentes externas, incluir URL directa, título, sección y fecha de consulta, y versión cuando sea relevante. Para código propio, enlazar archivo y símbolo; añadir revisión Git solo si existe. Usar rutas relativas para archivos del proyecto desde la entrada. Para cursos fuera del repositorio, conservar enlace local real y la ruta relativa a la biblioteca para poder encontrarlos en otra máquina.

Separar explícitamente:

- **Evidencia:** lo observado en una fuente.
- **Reconstrucción derivada:** el estado de código recompuesto y su nivel de certeza.
- **Interpretación:** lo que esa evidencia permite concluir y sus límites.
- **Adaptación:** lo que cambia por las necesidades del proyecto.
- **Propuesta propia:** lo que se decide sin atribuirlo al instructor.

## 6. Implementar y completar la entrada

Aplicar `filosofia-de-trabajo` dentro de la solicitud autorizada. Leer [assets/entrada.md](assets/entrada.md) antes de escribir una entrada de construcción; usar [assets/plan.md](assets/plan.md) para planes y [assets/fuente.md](assets/fuente.md) para fichas de fuentes. Adaptar las plantillas al tamaño real y eliminar secciones vacías. Para una implementación pequeña basta una entrada breve que mantenga la cadena fuente → decisión → código → comprobación.

Abrir una entrada `En curso` al comenzar el incremento que vaya a implementarse. Registrar objetivo, fuentes y decisiones propuestas; completar sobre el mismo archivo durante la implementación. No crear una nueva versión por cada intento o sesión del mismo incremento. Cada decisión sustantiva debe llegar a un archivo/símbolo cambiado o quedar expresamente descartada/pospuesta.

Explicar el mecanismo final, responsabilidades, flujo de datos, errores y razón de la elección. Referenciar el código del proyecto y fragmentos mínimos útiles, evitando mantener una copia completa que quede desactualizada. Anotar lo aprendido y los límites de las fuentes solo cuando ayuden a comprender el cambio.

Registrar únicamente las comprobaciones realmente ejecutadas, su resultado y lo pendiente. Diferenciar petición manual, compilación, prueba automatizada existente e inferencia. No crear suites amplias de tests por activar esta skill ni llamar probado a algo solo porque provenga de un curso; añadir tests nuevos cuando el usuario los solicite o sean parte expresa del incremento. Mantener secretos, tokens, datos personales y respuestas sensibles fuera del documento.

Cerrar como `Implementado y verificado` únicamente cuando el incremento y sus comprobaciones estén completos. Si falta ejecución, indicar `Implementado, pendiente de verificación`; si no hay código, `Investigación` o `Plan`; si un impedimento real corta el trabajo, `Bloqueado` con su causa. La numeración es documental y no equivale a una migración, versión de producto, commit ni tag.

## 7. Reanudar y reconstruir el historial

En futuras sesiones, volver a descubrir las tres áreas documentales. Ante una referencia como «02 de auth», resolver primero la carpeta y el archivo exactos; leer el documento objetivo, sus enlaces `Relacionada con`, las fuentes y planes asociados, la entrada anterior y la posterior de la misma secuencia cuando existan.

Usar `Fecha de creación`, `Última actualización` y la revisión Git registrada como anclas para reconstruir el momento. Consultar el historial Git del archivo y del código relacionado alrededor de esas fechas; distinguir claramente:

- lo que ya existía antes del documento;
- la decisión o plan registrado en ese momento;
- la implementación que lo materializó;
- los cambios posteriores que lo ampliaron o sustituyeron.

Contrastar siempre los documentos con el código actual. La bitácora, los planes y las fichas de fuentes conservan contexto histórico, pero no reemplazan el estado real del proyecto. No asumir que el mayor número es el trabajo activo ni que una fecha basta para atribuir causalidad.

Para una decisión que cambia después de cerrar el incremento, crear la siguiente entrada y enlazar la que sustituye o amplía, explicando qué evidencia cambió. Conservar la justificación histórica. Se pueden corregir erratas o enlaces rotos sin una nueva versión; señalar correcciones de evidencia que cambien el sentido. No atribuir cambios ajenos ni modificar documentos de otros trabajos en curso.

Antes de entregar, verificar fechas, enlaces, fidelidad de citas, secuencia en su carpeta, correspondencia con el diff y estados de verificación. Entregar enlaces a los documentos creados o actualizados y una frase con la decisión principal y su evidencia. No modificar Git, otras skills ni archivos de instrucciones para activar este comportamiento automáticamente; mantenerlo en el alcance de la skill y la petición actual.
