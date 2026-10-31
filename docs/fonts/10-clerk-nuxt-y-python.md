# 10 — Clerk: identidad Nuxt y verificación Python

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Investigación y adaptación frontend
Relacionada con: [base Nuxt](11-base-nuxt-y-cursos.md), [plan usuarios](../plans/02-api-identidad-y-usuarios.md)

Tipo de fuente: documentación oficial y código copiado. Consulta: 2026-10-30.

| ID | Fuente / localizador | Evidencia y aplicación |
| --- | --- | --- |
| C1 | [Nuxt Quickstart](https://clerk.com/docs/nuxt/getting-started/quickstart), install/module/keys | `@clerk/nuxt`, clave publicable en cliente y secret key en servidor. No ejecutar un aprovisionamiento de aplicación sin claves propias. |
| C2 | [useAuth](https://clerk.com/docs/nuxt/reference/composables/use-auth), return values | Estado y funciones reactivos del SDK; adaptador usa `getToken.value()` y `signOut.value()`. |
| C3 | [Session tokens](https://clerk.com/docs/guides/sessions/session-tokens), claims V2 | JWT de sesión con issuer/subject/fechas; email no es un campo garantizado por defecto. |
| C4 | [Python backend](https://clerk.com/articles/how-to-add-authentication-to-a-python-backend), FastAPI | SDK oficial verifica peticiones con headers y expone identidad verificada. Contrastar firmas con paquete instalado al implementar. |
| C5 | [Backend User](https://clerk.com/docs/reference/backend/types/backend-user) y [getUser](https://clerk.com/docs/reference/backend/user/get-user) | Perfil separado del JWT; email primario y nombres opcionales. JSON REST y SDK pueden usar nombres de campo diferentes. |

## Código existente y adaptación

Frontend origen: `/Users/benji/Documents/KSuT/estadistica-forms-web`, revisión `60e3f5982623d653353af92fcbfd68941909e442`. Se conservan `createAccessController`, `createProfileService` y estados de navegación. Se sustituye Descope por Clerk; no se copian hacks internos del SDK anterior.

Referencia de contratos backend: `/Users/benji/Documents/KSuT/claudeLearningAllPosibolIt`, HEAD `1f0be2d2e1b5c88f81eff801418cc739a543e0cb`, árbol de trabajo consultado. [UsersController](/Users/benji/Documents/KSuT/claudeLearningAllPosibolIt/src/users/users.controller.ts), `getCurrentUser`/`provisionCurrentUser`: identidad del guard y envoltorio GET/PUT `{user}`. [UsersService](/Users/benji/Documents/KSuT/claudeLearningAllPosibolIt/src/users/users.service.ts), `findCurrent`: perfil ausente como error. [UsersRepository](/Users/benji/Documents/KSuT/claudeLearningAllPosibolIt/src/users/users.repository.ts), `provision`/`findByIdentity`: UUID local y unicidad por emisor/sujeto. Interpretación: reutilizar contratos y responsabilidades, implementando validación Python; no copiar Nest como runtime ni atribuir todo el árbol de trabajo al commit indicado.

Estado real: módulo, componente y adaptador Clerk preparados en frontend. Faltan claves y backend autenticado, por lo que no hay login real de extremo a extremo comprobado. [API 02](../plans/02-api-identidad-y-usuarios.md) detalla validación y proyección en Turso.
