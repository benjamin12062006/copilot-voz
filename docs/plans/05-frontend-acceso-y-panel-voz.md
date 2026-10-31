# 05 — Frontend Nuxt: acceso, diseño y reproductor

Fecha de creación: 2026-10-30
Última actualización: 2026-10-31
Estado: En curso — dividido en [subplanes](frontend/01-tema-focus-y-espacio-de-trabajo.md); pantallas con datos simulados en [bitácora frontend 01](../../bitacora-construccion/frontend/01-pantallas-focus-nuxt-ui-y-clerk.md)
Relacionada con: [base y cursos](../fonts/11-base-nuxt-y-cursos.md), [Focus](../fonts/06-estilo-visual-focus-macos.md), [estados](../diagrams/03-estados-de-reproduccion.md)

## Condición de entrada

Ejecutar después de cerrar API 01–04. Ya se copió la base Nuxt de estadistica-forms-web a `frontend/`, se cambió el nombre y se adaptó el proveedor a Clerk. Esta preparación no es un panel Voz terminado ni una sesión real verificada.

## Traslado completo de la interfaz

Todo lo previsto antes para la interfaz de escritorio se implementará ahora en Nuxt/Vue: navegación lateral, Inicio, biblioteca, editor/importación, visor Markdown/Original, mensajes de error, selección y reproducción. Mantener estética Focus: superficies ciruela y gris violáceo, selección suave, filas sobrias, título amplio y cabecera geométrica propia. [Referencia](../fonts/06-estilo-visual-focus-macos.md). No imitar controles de ventana del sistema dentro de una web.

| Responsabilidad | Implementación Nuxt prevista |
| --- | --- |
| Navegación y composición | NuxtLayout/NuxtPage, layout del espacio de trabajo y páginas Inicio/Voz. |
| Biblioteca y borrador | Composable por funcionalidad y servicios HTTP; cambios no guardados visibles. |
| Lectura Markdown | Componentes para bloques del DTO preparado; Original literal, sin HTML remoto. |
| Reproducir | Descargar audio autorizado, Object URL y HTMLAudioElement tras acción del usuario. |
| Pausar | `audio.pause()` conserva posición. |
| Continuar | `audio.play()` sobre la misma sesión; manejar rechazo de la promesa. |
| Volver al inicio | `audio.currentTime = 0`; reproducir según acción explícita del botón. |
| Selección nueva/salir | Detener audio, invalidar intentos, abortar peticiones y revocar Object URL. |

No hay endpoints ni herramientas MCP para pausar, continuar o reiniciar. La API genera y entrega audio; Nuxt controla su reproducción y refleja eventos reales del elemento, incluyendo ended/error.

## Incrementos

1. Completar Clerk con claves propias y confirmar GET/PUT del perfil real, renovación única ante 401, recuperación y logout. Mantener el contrato copiado y el controlador legible. El middleware de ruta es navegación; la API sigue siendo quien autoriza.
2. Separar layout de acceso y layout de biblioteca cuando exista la pantalla que lo justifique. Crear Inicio sencillo con entrada Voz, lateral persistente y comportamiento en ventana estrecha. No añadir calendarios ni tarjetas sin función.
3. Biblioteca paginada y acciones crear/importar/guardar. Controlar estados de carga, error, vacío y conflicto; conservar borrador ante fallo. `.md` no se convierte por regex ni se trata como código ejecutable.
4. Visor con Original/Lectura, tipografía de cuerpo legible, ancho cómodo, avisos de preparación y componentes de tablas/listas. Incorporar accesibilidad/teclado desde el primer componente.
5. Reproductor único por espacio de trabajo: sesión de documento/revisión/voz, progreso escrito y controles explícitos. Estados preparando, listo, reproduciendo, pausado, terminado y error. Respuestas antiguas no sustituyen audio actual.
6. Mostrar documentos enviados desde Codex/Claude Code por MCP, usando la misma biblioteca de API. Refrescar al recuperar foco y durante trabajo activo. El MCP no gobierna los botones del reproductor ni inicia sonido sin interacción autorizada en el navegador.
7. Ajustar claro/oscuro y contraste, foco visible, movimiento reducido y lector de pantalla. La imagen Focus se conserva como referencia, no como activo redistribuido en la interfaz.

## Cierre previsto

`pnpm typecheck`, `pnpm lint`, `pnpm build` y comprobaciones de los recorridos reales: login → perfil → Voz; crear/importar ambos formatos → guardar → recargar; seleccionar → generar → reproducir → pausar → continuar → inicio. Cambiar selección durante una generación, salir de cuenta y error de red sin doble audio ni pérdida del borrador. Verificación visual con tamaños de ventana, teclado y contraste; no llamar terminada la UI solo porque compile.

Registrar por incremento archivos/símbolos, evidencia y resultado real. El diseño actual de acceso proviene del proyecto copiado; el rediseño Focus es trabajo pendiente de este plan.
