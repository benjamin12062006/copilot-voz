# 01 — Base Nuxt y acceso Clerk

Fecha de creación: 2026-10-30
Estado: Preparación implementada y verificada; acceso real pendiente
Ámbito: frontend Nuxt; registro histórico separado del backend por petición del usuario.
Relacionada con: [registro original de preparación](../backend/03-base-web-y-orden-api-frontend.md), [base Nuxt](../../docs/fonts/11-base-nuxt-y-cursos.md), [Clerk](../../docs/fonts/10-clerk-nuxt-y-python.md)

## Responsabilidad y preparación histórica

Este registro separa la parte de interfaz de la antigua entrada compartida 03; no representa una nueva implementación ni una nueva ejecución de comprobaciones. Otra IA continuará el frontend.

- Se copió app/public/configuración de estadistica-forms-web en `frontend/`, paquete copilot-web, sin claves ni Git de origen.
- Se sustituyó Descope por @clerk/nuxt: SignIn, plugin cliente, token del SDK y logout. Se conservaron controlador de acceso, estados y cliente de perfil GET/PUT.
- La configuración sin claves informa que falta Clerk. Un fallo de logout no se presenta como cierre confirmado; no hay JWT en estado SSR ni secretos Turso/Blob en el cliente.
- Navegación, componentes, interacción y reproducción de audio corresponden al frontend. Verificar identidad, guardar datos y sintetizar audio corresponde al backend.

## Comprobaciones históricas trasladadas

`pnpm typecheck`, `pnpm lint`, `pnpm format:check` y `pnpm build` fueron correctos según el registro original. El typecheck con clave publicable sintética también fue correcto; no demuestra login real. Esta reorganización no repitió comandos ni modificó archivos de `frontend/`.

El panel Focus y la conexión real corresponden al [plan frontend 05](../../docs/plans/05-frontend-acceso-y-panel-voz.md).
