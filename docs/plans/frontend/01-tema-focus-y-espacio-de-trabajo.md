# 01 — Tema Focus y espacio de trabajo con Nuxt UI

Fecha de creación: 2026-10-31
Estado: Implementado con datos simulados — [bitácora frontend 01](../../../bitacora-construccion/frontend/01-pantallas-focus-nuxt-ui-y-clerk.md)
Ámbito: frontend Nuxt
Relacionada con: [plan 05](../05-frontend-acceso-y-panel-voz.md), [Nuxt UI](../../fonts/frontend/01-nuxt-ui-instalacion-y-tema.md), [Focus](../../fonts/06-estilo-visual-focus-macos.md)
Revisión de referencia: `663e454` (`v0.2.0`)

## Objetivo

Que la aplicación se vea como la referencia Focus: lateral gris violáceo con secciones y contadores, panel ciruela con cabecera ilustrada, título grande y fino y filas con separadores tenues. Todo se construye sobre componentes de Nuxt UI, con Tailwind solo donde haga falta.

## Punto de partida

La base copiada usa Roboto, una paleta verde y un layout de tarjeta centrada. Ya incluye Tailwind 4 y no tiene librería de componentes.

## Decisiones

- Colores medidos de la captura: lateral `#4c4551`, fila activa `#5f5661`, tarjeta `#6b626d`, principal `#362e38`, separador `#3e3640`, texto `#fbf7fb`, atenuado `#978d9b`, etiquetas `#89808d`. Se aplican a las variables `--ui-*` en `.dark`; claro es variante propia.
- Tipografía del sistema (`-apple-system`/SF en macOS) con títulos en peso 300, como la referencia.
- `ui.fonts: false` e iconos Lucide locales, para no depender de la red.
- Cabecera ilustrada en SVG propio (`FocusCover`), con curvas superpuestas en los colores medidos (salvia, mostaza, malva, azul, lavanda, melocotón, naranja, rojo). No se copia la imagen.
- `UDashboardGroup` + `UDashboardSidebar` (plegable y menú móvil) + `UDashboardPanel`. No se dibujan semáforos de ventana.

## Incrementos

1. Instalar Nuxt UI, `UApp`, CSS de tokens y modo oscuro por defecto.
2. Layout `workspace`: lateral con tarjetas «Todos/Agentes», navegación (Inicio, Voz, Cuenta), sección «Formatos» con puntos de color y usuario al pie.
3. Componente `FocusCover` y estructura de página «cabecera + título + filas».
4. Layout `access` para entrar y sesión, con la misma estética.

## Comprobación prevista

`pnpm typecheck`, `pnpm lint`, `pnpm build`; captura a 1280 px comparada con la referencia, ventana estrecha (menú móvil), foco visible y modo claro.
