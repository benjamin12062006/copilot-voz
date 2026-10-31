# 02 — API: Clerk y perfiles en Turso

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [fuentes Clerk](../fonts/10-clerk-nuxt-y-python.md), [fuentes Turso](../fonts/12-turso-usuarios-python.md)

## Objetivo

Proteger la API y entregar exactamente el contrato de perfil que ya consume la base Nuxt copiada. Depende del cierre de [API 01](01-api-base-y-configuracion.md). Primero comprobar con peticiones HTTP; la UI completa llega después.

## Fuentes y adaptación

Reutilizar el mecanismo GET/PUT y unicidad por emisor/sujeto de los proyectos de referencia, documentado en [Clerk](../fonts/10-clerk-nuxt-y-python.md) y [antecedentes SQL](../fonts/13-antecedentes-api-recuperados.md). Adaptar a Python y Turso; no copiar Prisma, guards Nest ni autenticación Descope.

## Incrementos

1. Añadir el SDK oficial `clerk-backend-api` y verificar API/tipos instalados. Autenticar solicitudes Bearer aceptando solo session tokens; comprobar firma, expiración/not-before, emisor esperado y authorized parties de los orígenes Nuxt. No basta decodificar JWT. Un SDK que no imponga emisor exacto requiere comprobarlo explícitamente tras verificación.
2. Modelar identidad con `issuer` y `subject` verificados. La aplicación es personal: permitir los Clerk user IDs configurados; el resto recibe 403. No asignar permisos por un email recibido del cliente.
3. Confirmar motor de la base Turso antes de elegir driver: `turso_serverless` para motor Turso remoto `turso://`; `libsql` para base libSQL `libsql://`. Instalar solo el adecuado, comprobar wheel/conexión y fijar lock. [Documentación](../fonts/12-turso-usuarios-python.md).
4. Crear migración SQL de `app_users`, basada en el esquema recuperado: UUID local, issuer, subject, email/nombre opcionales y fechas. Registrar migraciones aplicadas; SQL parametrizado y transacciones. Verificar esquema antes de marcar una migración aplicada. No ejecutar sobre una base ajena.
5. Implementar repositorio y aprovisionamiento idempotente con unicidad de issuer/subject, incluyendo dos solicitudes simultáneas. Un 404 de perfil significa ausencia, no fallo de autenticación.
6. Completar datos desde Clerk Backend User cuando haga falta: email primario por su ID, verificación si la política la exige, nombre compuesto de campos opcionales. El JWT no garantiza email. No permitir que un body decida issuer/subject. La indisponibilidad del proveedor debe ser error explícito al aprovisionar; conservar perfil existente al leer.
7. Devolver alias JSON camelCase, aunque Python use snake_case. No devolver secretos ni identidad interna innecesaria.

## Contrato a implementar

| Método y ruta | Respuesta |
| --- | --- |
| `GET /api/v1/auth/me` | `{identity:{subject,issuer}}`, solo identidad verificada. |
| `GET /api/v1/users/me` | 200 `{user:{id,email,displayName,createdAt,updatedAt}}`; 404 si aún falta. |
| `PUT /api/v1/users/me` | 200 mismo envoltorio, exista o se cree; body vacío. |

Email y displayName pueden ser null; fechas UTC ISO-8601. No añadir endpoint de contraseñas. Webhooks firmados de Clerk para cambios/borrado quedan para una evolución separada; ahora aprovisionamiento al primer acceso.

## Cierre previsto

Sin token, firma inválida, expirado o issuer incorrecto → 401. Usuario válido fuera de allowlist → 403. GET ausente → 404; PUT repetido/concurrente → un mismo ID; luego GET → mismo perfil. Comprobar nulos, fechas y caída de Turso sin perfil ficticio. Una sesión real válida requiere claves de Clerk; ejecutar casos controlados de integración antes de declarar cierre.

Guardar evidencia y respuestas sanitizadas; pasar a [API 03](03-api-documentos-blob-y-markdown.md).
