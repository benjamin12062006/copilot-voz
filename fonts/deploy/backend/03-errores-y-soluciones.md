# 03 — Errores encontrados y soluciones comprobadas

Fecha de creación: 2026-10-31
Estado: Registro de diagnóstico
Relacionada con: [procedimiento](01-procedimiento-fastapi-vercel.md), [investigación](02-investigacion-y-decisiones.md)

## Anotaciones y Python 3.12

Síntoma: `TypeError: 'function' object is not subscriptable` al importar `DocumentStore`.

Causa: el método `list` ocultaba el builtin del mismo nombre al evaluar `list[RetiredFile]` dentro de la clase. En el entorno Python 3.14 previo no aparecía ese error al importar.

Solución: `from __future__ import annotations` al comienzo de `backend/app/documents.py`. Las 29 pruebas volvieron a pasar en Python 3.12. No se renombró el método ni se cambió el contrato de documentos. Commit: `3b08882`.

## Sesión antigua y desafío de autenticación

La sesión inicial del CLI permitía consultar y crear proyectos, pero descargar variables y crear tokens devolvía `challenge_required`. Se ejecutó el CLI oficial `vercel login`; el usuario aprobó el flujo de dispositivo. Después se pudo descargar la configuración del proyecto y desplegar.

No guardar ni reutilizar el código de dispositivo: es temporal. No reemplazar una sesión válida por credenciales de otra cuenta.

## Token de automatización

Después de renovar la sesión, el API y el comando oficial de tokens respondieron `Cannot create tokens for this app`. La aplicación OAuth del CLI no puede generar ese token personal.

Solución: el usuario lo creó en [Vercel Tokens](https://vercel.com/account/settings/tokens) y lo guardó directamente en los secretos de GitHub. Las variables del proyecto y el despliegue inicial se completaron mientras tanto. No reutilizar el token general de la sesión local como alternativa silenciosa.

## Primer workflow sin secreto

El workflow falló en su comprobación inicial porque todavía faltaba `VERCEL_BACKEND_TOKEN`. Ese fallo era de configuración, anterior al build. Después de que el usuario guardó el secreto, se ejecutó de nuevo con `workflow_dispatch`.

## Colisión entre `.vercelignore` y el bundle precompilado

Síntoma: publicación prebuilt fallida con `ENOENT`, al resolver un enlace a `01-preparacion.md`.

Causa: `vercel build` había trazado ese documento como parte de la función, mientras `.vercelignore` impedía subirlo. El CLI mostró una advertencia indicando el archivo y la regla que colisionaban. El build podía terminar correctamente y aun así fallar la publicación.

Solución: agregar `01-preparacion.md` al patrón `functions.app/main.py.excludeFiles` de `backend/vercel.json`, además de ignorarlo al subir fuentes. Se reconstruyó y se verificó la publicación desde Actions. Commit: `aa5694c`.

Regla práctica: si se excluye un archivo del upload, excluirlo también del tracing del bundle cuando el builder lo haya incluido. No quitar exclusiones de credenciales para hacer pasar un deploy.

## URL de producción y protección de despliegues

La URL única de cada despliegue puede mostrar autenticación de Vercel. Para la comunicación pública frontend/backend se usa el alias estable `https://copilot-backend-navy.vercel.app`, cuyo `/health` se comprobó sin bypass.

El workflow publica con `--json`, extrae `deployment.productionUrl` cuando existe y acepta el formato alternativo de URL. No asumir que la última línea de salida será siempre la URL; puede ser JSON. Los datos de negocio siguen protegidos por Clerk y los tokens personales de la API.

## Protección de secretos

La revisión automática pidió autorización explícita para transferir valores de `.env` a Vercel y crear una credencial en GitHub. El usuario autorizó ambos destinos antes de efectuar la copia. Se mantuvieron los valores fuera del chat, el repositorio y los documentos.

`.vercel/` contiene configuración y variables descargadas: siempre debe permanecer ignorado. Los comandos usan `VERCEL_TOKEN` desde el entorno. No activar `set -x` ni imprimir archivos de autenticación para diagnosticar fallos.
