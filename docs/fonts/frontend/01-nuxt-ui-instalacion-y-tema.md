# 01 — Nuxt UI: instalación, tema y componentes

Fecha de creación: 2026-10-30
Tipo de fuente: documentación oficial y paquete instalado
Origen: Nuxt UI (ui.nuxt.com), versión 4.12.0
Fecha de consulta: 2026-10-30
Relacionada con: [plan frontend 01](../../plans/frontend/01-tema-focus-y-espacio-de-trabajo.md), [dirección visual Focus](../06-estilo-visual-focus-macos.md)

## Necesidad de consulta

El usuario eligió Nuxt UI como base de componentes para reproducir la referencia Focus tocando poco cada componente y completando con Tailwind.

## Localización verificable

| ID | Fuente | Sección |
| --- | --- | --- |
| U1 | [Installation · Nuxt](https://ui.nuxt.com/docs/getting-started/installation/nuxt) | Install, Register module, Import CSS, Wrap with App, Options |
| U2 | [CSS Variables](https://ui.nuxt.com/docs/getting-started/theme/css-variables) | Colors, Text, Background, Border, Radius; `:root` y `.dark` |
| U3 | [Components](https://ui.nuxt.com/docs/components) | Catálogo |
| U4 | Paquete instalado `node_modules/@nuxt/ui/dist/runtime/components/*.vue.d.ts` | Props y slots de DashboardSidebar, DashboardPanel, NavigationMenu, Tabs, FileUpload, Empty, Slider |

## Evidencia

- **U1:** instalar `@nuxt/ui` y `tailwindcss`, registrar el módulo, crear un CSS con `@import "tailwindcss";` seguido de `@import "@nuxt/ui";` y envolver la app con `UApp`, necesario para Toast, Tooltip y overlays. El módulo registra `@nuxt/icon`, `@nuxt/fonts` y `@nuxtjs/color-mode`. La opción `fonts` se puede desactivar.
- **U2:** el tema se ajusta con variables `--ui-bg`, `--ui-bg-muted`, `--ui-bg-elevated`, `--ui-bg-accented`, `--ui-text*`, `--ui-border*` y `--ui-radius`, sobrescritas en `:root` (claro) y `.dark` (oscuro) después de los imports.
- **U4:** 4.12.0 incluye `DashboardGroup/Sidebar/Panel` (lateral plegable con menú móvil), `NavigationMenu` vertical con badges, `Tabs`, `FileUpload` con `accept`, `Empty`, `Slider`, `User`, `Toast` y `ColorModeButton`.

## Interpretación y límites

La documentación no fija colores para una marca concreta; los valores salen de medir píxeles de la captura Focus ([ficha 06](../06-estilo-visual-focus-macos.md)). Las páginas consultadas no explican cómo definir una paleta propia en `app.config`; se usa `violet` como `primary` y las superficies se fijan con las variables U2.

## Aplicación en el proyecto

- `nuxt.config.ts`: módulo `@nuxt/ui`, `ui.fonts: false` (tipografía del sistema, como macOS, sin descargas en build) y modo de color oscuro por defecto.
- `app/assets/css/main.css`: tokens Focus medidos sobre `--ui-*` en `.dark` y una variante clara en `:root`.
- Iconos `i-lucide-*` resueltos localmente con `@iconify-json/lucide`, para no depender de la API de Iconify en tiempo de ejecución.
