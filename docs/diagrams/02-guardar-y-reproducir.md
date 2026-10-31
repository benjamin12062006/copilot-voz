# 02 — Enviar, guardar, generar y reproducir

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [documentos](../plans/03-api-documentos-blob-y-markdown.md), [voz y MCP](../plans/04-api-voz-y-mcp.md), [Nuxt](../plans/05-frontend-acceso-y-panel-voz.md)

Secuencia prevista para el recorrido por Nuxt y para el ingreso alternativo desde un agente.

```mermaid
sequenceDiagram
  actor U as Usuario
  participant N as Nuxt / Vue
  participant A as FastAPI
  participant B as Blob privado
  participant P as Preparador + TTS Python
  participant C as Codex o Claude Code
  participant M as MCP stdio Python
  Note over A: Identidad verificada; perfil Turso creado en API 02
  alt Documento desde Nuxt
    U->>N: Crear o importar MD/TXT
    N->>A: Guardar con JWT
    A->>A: Autorizar y validar
    A->>B: Escribir documento y metadata juntos
    B-->>A: Confirmación + ETag
    A-->>N: Documento guardado + revision
  else Documento desde agente
    C->>M: voice_submit_document
    M->>A: Envío con token limitado de agente
    A->>A: Resolver propietario fijo y validar
    A->>B: Guardar idempotentemente
    B-->>A: Confirmación
    A-->>M: documentId + revision
    M-->>C: Guardado, no reproducido
    N->>A: Refrescar biblioteca autorizada
    A-->>N: Documento nuevo disponible
  end
  U->>N: Seleccionar y pedir audio
  N->>A: Crear job de síntesis
  A->>P: Preparar revisión y generar audio
  A-->>N: Job queued/running
  P-->>A: Audio completo disponible
  N->>A: Consultar job y descargar audio autorizado
  A-->>N: Binario de audio
  N->>N: Crear Object URL
  U->>N: Reproducir
  N->>N: audio.play()
  U->>N: Pausar / continuar / volver al inicio
  N->>N: pause() / play() / currentTime = 0
  Note over N: Controles locales de Nuxt, sin llamadas MCP ni API
  opt Agente pidió también generar audio
    C->>M: voice_get_status(jobId)
    M->>A: Consultar estado autorizado
    A-->>M: ready / failed / expired
    M-->>C: Estado de generación, no de reproducción
  end
```

Reintentos de envío usan clave idempotente asociada al propietario y fingerprint del contenido. Una misma clave con contenido diferente devuelve conflicto. Un job listo puede ser consumido por Nuxt; generar desde MCP no habilita autoplay. El esquema omite detalles de transporte; las rutas propuestas están en planes 02–04.
