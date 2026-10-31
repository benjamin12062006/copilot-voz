# 02 — Requisitos y recorrido

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [alcance](01-proposito-y-alcance.md), [estados de audio](../diagrams/03-estados-de-reproduccion.md)

| ID | Resultado esperado | Incremento |
| --- | --- | --- |
| R01 | La API valida configuración y ofrece salud sin depender de la UI. | API 01 |
| R02 | Clerk verifica sesiones; Turso identifica usuario por emisor y sujeto únicos. | API 02 |
| R03 | GET del perfil devuelve 404 si falta; PUT lo aprovisiona idempotentemente. | API 02 |
| R04 | Crear, listar y recuperar documentos propios en Blob privado. | API 03 |
| R05 | Admitir texto plano y Markdown UTF-8, conservar original y formato. | API 03 |
| R06 | Preparar bloques visuales, texto hablado y avisos desde un solo parser. | API 03 |
| R07 | Generar audio español y servirlo al propietario; limitar recursos. | API 04 |
| R08 | MCP expone capacidades acotadas reutilizando servicios de aplicación. | API 04 |
| R09 | Inicio simple y navegación lateral con entrada Voz. | Frontend 05 |
| R10 | Biblioteca, editor, Original/Lectura y controles de audio visibles. | Frontend 05 |
| R11 | Reproducir, pausar, continuar y volver al inicio sin audio simultáneo. | Frontend 05 |
| R12 | Acceso por teclado, contraste y lectura cómoda con diseño Focus adaptado. | Frontend 05 |

## Recorrido futuro

Entrar → confirmar sesión → GET perfil → si 404, PUT perfil → Inicio → Voz. Crear/importar genera un borrador en memoria. Guardar confirma escritura remota antes de marcarlo como guardado. Un fallo conserva el borrador; no comunica éxito ni cambia a un almacén alternativo.

Seleccionar documento → obtener original/version → preparar → mostrar lectura y avisos → generar audio → reproducir en el navegador tras acción del usuario. Cambiar de selección detiene audio y cancela solicitudes; una respuesta tardía no puede reproducir el documento anterior.

Pausa llama a `audio.pause()`, continuar usa `audio.play()` y reinicio vuelve a tiempo cero del audio de la sesión actual. La síntesis es distinta de la reproducción: la pausa no necesita una petición MCP. Cerrar sesión detiene audio, vacía estado privado en memoria y confirma el resultado real del SDK.

## Errores visibles

401: sesión ausente/caducada; 403: identidad válida sin acceso personal permitido; 404: recurso inexistente o ajeno; 409: versión obsoleta; 413: límite de tamaño; 422: formato/codificación/contenido inválido; 503: proveedor no disponible. La UI solo reintenta automáticamente una vez al renovar token tras 401. Guardados y generación de audio no se repiten ciegamente.

La API impone propiedad aunque el middleware de Nuxt deje navegar. Nunca aceptar el usuario propietario desde un campo enviado por el cliente.
