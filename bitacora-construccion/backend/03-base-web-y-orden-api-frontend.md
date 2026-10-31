# 03 — Backend separado y planes de ejecución

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Preparación implementada y verificada; producto funcional pendiente
Ámbito: backend e integración; detalle de interfaz trasladado a frontend.
Relacionada con: [índice](../../docs/01-indice.md), [antecedente](02-preparacion-upstash.md), [base frontend](../frontend/01-base-nuxt-y-acceso.md)

## Necesidad y evidencia

El usuario cambió el stack a Nuxt/pnpm y FastAPI/Python, eligió Clerk, corrigió usuarios a Turso y mantuvo documentos en Blob. Solicitó reutilizar el proyecto web existente, fuentes históricas y filosofía de legibilidad; después pidió retirar la tecnología inicial y ejecutar primero API y luego frontend.

La [base Nuxt y sus cursos](../../docs/fonts/11-base-nuxt-y-cursos.md) respaldan layout/composables/middleware; [Clerk](../../docs/fonts/10-clerk-nuxt-y-python.md) respalda el nuevo adaptador. Los contratos GET/PUT y la identidad local se recuperan de código propio e [historial de API](../../docs/fonts/13-antecedentes-api-recuperados.md). El diseño de casos de uso y la secuencia de planes son adaptación propia.

## Preparación implementada

- Contrato de integración con Nuxt conservado: perfil GET/PUT y sesión Bearer. La preparación de pantallas, componentes y estados pertenece al [registro frontend](../frontend/01-base-nuxt-y-acceso.md).
- Entorno Python y uv.lock en `backend/`, separado de Nuxt. No hay rutas de producto implementadas.
- Plugin Turso instalado y activado solo para el proyecto; OAuth pendiente. La skill construir-con-evidencia está local al proyecto. La documentación sigue en raíz y la bitácora se separó posteriormente en `backend/` y `frontend/` por petición del usuario, conservando los números históricos del backend.
- Fuentes antiguas recuperadas con git show y manifiesto SHA-256, sin cambiar rama/tag del repositorio original ni su trabajo pendiente.
- Eliminados archivos/fuentes específicos de la tecnología descartada. Sustituidos planes por cinco pasos API→frontend; actualizado producto, fuentes y tres diagramas.
- MCP propio planificado para Codex y Claude Code con plantillas inactivas. Solo envío de contenido/listado/estado; todos los controles de audio y toda la interfaz pertenecen a Nuxt.

## Estado de comprobación

Comprobaciones finales ejecutadas:

| Comprobación | Resultado |
| --- | --- |
| Backend: `uv sync --locked --offline` e imports FastAPI/pydantic-settings/upstash-blob | Correctos usando caché temporal permitida; un intento previo con caché global fue rechazado por el sandbox. |
| Documentación: 28 Markdown, metadatos y enlaces locales | Fechas presentes, destinos existentes y sin referencias de la tecnología retirada. |
| Inventarios de planes/fuentes | Planes 01–05 en orden, sin prefijos duplicados. Fuentes mantienen sus números históricos con huecos tras retirar fichas. |
| Plantillas TOML/JSON y manifiesto de fuentes | Sintaxis válida y hashes de las cuatro copias correctos. |
| API de origen | HEAD, rama, estado, diff y diff staged idénticos al registro inicial; no hubo checkout. |
| `git diff --check` y búsqueda de archivos de la tecnología retirada | Sin errores de espacios ni archivos residuales en el árbol de trabajo. |

No hay login real, perfiles Turso, documentos Blob, generación de audio ni handshake MCP comprobados: esos componentes funcionales siguen pendientes. La CLI Claude Code no está en PATH; su conexión queda para API 04. No se guardaron claves ni se crearon recursos remotos.

## Continuidad

Comenzar por [API 01](../../docs/plans/01-api-base-y-configuracion.md), cerrar su aceptación y avanzar en orden. El panel Focus se ejecuta en [Frontend 05](../../docs/plans/05-frontend-acceso-y-panel-voz.md). No se crearon commits/tags; cambios staged previos y eliminaciones del usuario se conservan.
