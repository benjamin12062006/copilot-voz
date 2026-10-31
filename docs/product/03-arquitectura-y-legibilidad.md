# 03 — Arquitectura y legibilidad

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [fuentes de legibilidad](../fonts/04-contrato-voz-y-filosofia.md), [contexto](../diagrams/01-contexto-y-responsabilidades.md)

## Responsabilidades

Nuxt se ocupa de navegación, componentes, estado de interacción y reproducción de audio. FastAPI verifica identidad, valida entradas y coordina documentos, perfiles y síntesis. Los adaptadores Turso, Blob y voz concentran detalles de proveedor. MCP es otra entrada a los mismos servicios, no una segunda implementación del negocio.

Mapa propuesto, a crear conforme llegue cada incremento:

```text
backend/
  app/
    main.py                 composición y lifespan
    settings.py             carga y validación de entorno
    auth/                   verificación Clerk e identidad
    users/                  rutas, servicio y repositorio Turso
    documents/              rutas, servicio, preparación y adaptador Blob
    speech/                 generación y entrega de audio
    mcp/                    herramientas que llaman los servicios existentes
  migrations/               SQL versionado y registro de aplicación
frontend/
  app/
    pages/                  rutas Nuxt
    layouts/                estructura compartida
    components/             piezas visuales
    composables/            estado y acciones de la interfaz
    services/               HTTP y coordinación de acceso
    types/                  contratos realmente compartidos
```

Las carpetas del backend son una propuesta; todavía no existen. El frontend conserva la estructura copiada. No crear archivos vacíos para completar el dibujo. Separar módulo solo cuando haya una responsabilidad que ayude a leer o sustituir una dependencia.

## Lectura humana

La filosofía del usuario exige métodos principales que se lean de arriba abajo. Ejemplo: guardar documento se expresa como autorizar → validar borrador → construir registro → escribir con condición de versión → devolver confirmación. El detalle de las consultas y del SDK queda próximo a su adaptador. Evitar helpers que solo cambien el nombre de una operación, cadenas densas y DTO idénticos por capa. [Fundamento](../fonts/04-contrato-voz-y-filosofia.md).

Cada incremento debe explicar recorrido, archivos/símbolos, una decisión y su comprobación. Distinguir una regla heredada del código de referencia de una propuesta nueva. No atribuir Clerk, Turso Python o MCP a cursos que no los enseñan.

## Estado y concurrencia

Una identidad verificada viaja por petición, sin variables globales de usuario. Los clientes externos se abren y cierran en lifespan cuando el SDK lo permita. No bloquear el event loop con SQL síncrono o inferencia pesada: repositorio síncrono ejecutado en el mecanismo de threads de FastAPI; síntesis en trabajo acotado con cola/concurrencia limitada tras medir el modelo.

El frontend conserva identificadores de intento para descartar resultados tardíos. La sesión de audio captura documento, revisión y opciones. Cambiar texto no modifica audio que ya fue generado: invalida la sesión y requiere nueva generación. Los tokens del SDK no se copian a estado SSR ni se guardan manualmente en localStorage.

## Límites de confianza

Clerk autentica; la API aplica permisos. Turso/Blob/Clerk secret keys solo viven en servidores. No incluirlos en `runtimeConfig.public`. La entrada MCP valida su propia autorización y nunca permite shell, rutas arbitrarias o eludir la propiedad de un documento. [MCP y voz](../fonts/14-voz-python-y-mcp.md).
