# 04 — Conectar frontend y backend: URLs, variables y CORS

Fecha de creación: 2026-10-31
Estado: Implementado y verificado
Relacionada con: [backend](01-procedimiento-fastapi-vercel.md), [frontend](../frontend/01-procedimiento-nuxt-vercel.md), [diagnóstico](03-errores-y-soluciones.md)
Revisión de referencia del backend: `aa5694c`.

## URLs estables

| Uso | URL |
| --- | --- |
| Interfaz web | `https://copilot-frontend-lovat.vercel.app` |
| API base para el frontend y los clientes MCP | `https://copilot-backend-navy.vercel.app/api/v1` |
| Salud del backend | `https://copilot-backend-navy.vercel.app/health` |

Las URLs con hashes que Vercel asigna a cada despliegue son útiles para diagnóstico; la configuración de producción usa los alias estables. No agregar comodines de `vercel.app` a CORS ni usar una URL de preview que cambiará en el siguiente build.

## Variables del frontend en Vercel Production

```text
NUXT_PUBLIC_API_BASE_URL=https://copilot-backend-navy.vercel.app/api/v1
NUXT_PUBLIC_DATA_SOURCE=api
NUXT_PUBLIC_PREVIEW_SESSION=false
NUXT_PUBLIC_CLERK_KEYLESS_DISABLED=true
```

La clave publicable `NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY` se configura tanto para compilar como para ejecutar. `NUXT_CLERK_SECRET_KEY` permanece como secreto del proyecto. Se copió la instancia Clerk existente con autorización del usuario, para conservar su identidad y sus datos.

Se comprobó que el host codificado en la clave publicable del frontend corresponde exactamente a `CLERK_ISSUER` del backend. No basta con que ambos tengan una clave válida si pertenecen a instancias distintas.

## Variables del backend en Vercel Production

Ambas listas contienen los mismos orígenes exactos:

```text
COPILOT_CORS_ORIGINS=["https://copilot-frontend-lovat.vercel.app","http://localhost:3000","http://127.0.0.1:3000"]
CLERK_AUTHORIZED_PARTIES=["https://copilot-frontend-lovat.vercel.app","http://localhost:3000","http://127.0.0.1:3000"]
```

`COPILOT_CORS_ORIGINS` permite al navegador leer la respuesta. `CLERK_AUTHORIZED_PARTIES` comprueba el claim `azp` del JWT. Son controles diferentes: que pase el preflight no sustituye la sesión válida.

Cada origen lleva esquema y host, sin `/api/v1`, rutas ni barra final. El frontend envía `Authorization: Bearer …`; el backend permite ese header, `Content-Type` y los métodos necesarios. No requiere cookies entre los dos dominios y mantiene `allow_credentials=False`.

Se conserva `copilot/dev`, la base Turso y el bucket existentes. No se ejecutaron migraciones como parte de enlazar los servicios. Las variables locales de desarrollo conservan sus destinos locales; las plantillas `.env.production.example` registran la configuración de despliegue sin secretos.

## Orden para aplicar cambios

1. Configurar el frontend con la URL real del backend y las claves de la misma instancia Clerk.
2. Desplegar el frontend y obtener su alias estable.
3. Guardar ese origen en las dos listas del backend.
4. Ejecutar de nuevo el workflow del backend: cambiar variables no modifica funciones ya desplegadas.
5. Reintentar la sesión del frontend y comprobar preflight y rutas privadas.

## Comprobaciones

- `/auth` del frontend devuelve HTML y contiene la URL correcta de API.
- El HTML público contiene configuración publicable de Clerk y no contiene la clave secreta.
- `/health` del backend responde 200.
- El preflight de `/api/v1/documents` con el origen del frontend debe responder 200 e incluir ese origen en `Access-Control-Allow-Origin`.
- Un origen ajeno debe recibir 400 sin `Access-Control-Allow-Origin`.
- Una petición privada sin sesión sigue respondiendo 401, incluso desde un origen permitido.
- Con sesión real, el frontend debe completar `/session` y obtener la cuenta desde el backend.

Resultados observados el 2026-10-31: HTML del frontend 200 con la URL API correcta; sin clave secreta en el HTML; preflight del origen permitido 200 con `Access-Control-Allow-Origin` exacto; origen ajeno 400 sin esa cabecera. Tras [publicar las nuevas variables con Actions](https://github.com/benjamin12062006/copilot-voz/actions/runs/41177622994), el navegador completó `/session`, llegó a `/home` y cargó la biblioteca existente. Esto comprobó una sesión real y lecturas a través de ambos servicios; no se crearon documentos para la prueba.

Si el frontend aparece en `/session` con un error inmediatamente después de cambiar CORS, esperar a que termine el despliegue del backend y reintentar. No ampliar permisos para ocultar una configuración que todavía no se ha publicado.
