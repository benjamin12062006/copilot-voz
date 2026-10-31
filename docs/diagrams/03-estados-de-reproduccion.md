# 03 — Estados del reproductor Nuxt

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [plan frontend](../plans/05-frontend-acceso-y-panel-voz.md), [requisitos](../product/02-requisitos-y-recorrido.md)

Estado de interfaz y audio local. Los estados del job de síntesis del backend son independientes: queued/running/ready/failed/expired.

```mermaid
stateDiagram-v2
  [*] --> SinSeleccion
  SinSeleccion --> Seleccionado: Elegir documento
  Seleccionado --> PreparandoAudio: Solicitar generación o recuperar job
  PreparandoAudio --> Listo: Audio descargado de la revisión actual
  PreparandoAudio --> Error: Fallo de preparación, síntesis o descarga
  Listo --> Reproduciendo: Usuario pulsa reproducir / play resuelto
  Reproduciendo --> Pausado: pause() y evento pause
  Pausado --> Reproduciendo: play() resuelto
  Reproduciendo --> Terminado: evento ended
  Terminado --> Reproduciendo: Usuario pulsa desde el inicio
  Pausado --> Reproduciendo: Usuario pulsa desde el inicio
  Reproduciendo --> Reproduciendo: Usuario pulsa desde el inicio
  Reproduciendo --> Error: evento error
  Pausado --> Error: fallo de audio
  Listo --> Error: play rechazado
  Error --> PreparandoAudio: Reintento explícito
  Seleccionado --> SinSeleccion: Salir de cuenta
  PreparandoAudio --> SinSeleccion: Salir de cuenta
  Listo --> SinSeleccion: Salir de cuenta
  Reproduciendo --> SinSeleccion: Salir de cuenta
  Pausado --> SinSeleccion: Salir de cuenta
  Terminado --> SinSeleccion: Salir de cuenta
  Error --> SinSeleccion: Salir de cuenta
```

Al cambiar documento desde cualquier estado: detener audio previo, abortar peticiones, invalidar intento y volver a Seleccionado. Al salir: además revocar Object URL y vaciar datos privados. Reiniciar establece tiempo cero del mismo audio; no pide volver a sintetizar. Reflejar eventos reales del elemento y errores de `play()`; no dar por iniciada una reproducción porque el backend haya terminado el job.

Estos controles y toda la pantalla se implementarán en Nuxt/Vue. MCP solo envía documentos y consulta procesamiento.
