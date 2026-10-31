# 03 — Biblioteca, editor e importación con datos simulados

Fecha de creación: 2026-10-31
Estado: Implementado con datos simulados — [bitácora frontend 01](../../../bitacora-construccion/frontend/01-pantallas-focus-nuxt-ui-y-clerk.md)
Ámbito: frontend Nuxt, documentos
Relacionada con: [plan 05 incrementos 3 y 6](../05-frontend-acceso-y-panel-voz.md), [API 03](../03-api-documentos-blob-y-markdown.md), [datos y formatos](../../product/04-datos-y-formatos.md)

## Objetivo

Listar, crear, importar, editar y guardar documentos con todos los estados visibles (cargando, vacío, error, conflicto, cambios sin guardar), simulando la API que llegará en API 03.

## Decisiones

- Contrato `DocumentService` en `types/documents.ts` (list, get, create, update, prepare). Por ahora solo existe una implementación simulada en memoria, con latencia y con documentos de ejemplo enviados por la web y por agentes MCP.
- La preparación de Markdown (bloques para leer y texto hablado) pertenece a la API. El simulador la imita con el lexer de `marked`, y solo dentro de `services/mock/`, para poder borrarlo entero al conectar la API. La interfaz recibe bloques ya preparados y nunca interpreta HTML.
- Guardar usa `revision`: si cambió, responde «conflicto» y el borrador se conserva.
- Importación con `UFileUpload`, solo `.md` y `.txt`, UTF-8 y hasta 1 MiB, igual que `COPILOT_STORAGE_MAX_DOCUMENT_BYTES`.
- La biblioteca se refresca al recuperar el foco de la ventana, para que aparezcan los documentos enviados por agentes.

## Incrementos

1. Tipos, servicio simulado y plugin que lo provee.
2. `/voice`: lista estilo Focus con formato, origen, fecha y estados.
3. `/voice/new`: título, formato y contenido, con importación y aviso de cambios sin guardar.
4. Edición dentro del documento con detección de conflicto.

## Comprobación prevista

Recorrido en navegador: crear → guardar → aparece en la lista; importar `.md`; editar → conflicto simulado → el borrador se conserva; estados vacío y error forzados.
