# 14 — Síntesis Python, reproductor Nuxt y MCP

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Investigación; motores y MCP sin implementar
Relacionada con: [API voz/MCP](../plans/04-api-voz-y-mcp.md), [frontend](../plans/05-frontend-acceso-y-panel-voz.md)

Tipo de fuente: repositorios primarios y documentación oficial. Consulta: 2026-10-30.

| ID | Fuente y sección | Evidencia / límite |
| --- | --- | --- |
| V1 | [Kokoro](https://github.com/hexgrad/kokoro), README; [voces](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md) | Modelo de 82M parámetros y voces españolas; no demuestra calidad ni rendimiento en este equipo. |
| V2 | [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), examples/setup | Wrapper Python ONNX a evaluar por compatibilidad, memoria y latencia. No es el repositorio oficial del motor original. |
| V3 | [Piper](https://github.com/OHF-Voice/piper1-gpl), README | Alternativa local rápida; revisar licencia GPL del motor y licencia particular de cada voz antes de distribuir. |
| V4 | [HTMLMediaElement](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement), play/pause/currentTime | Reproducción, pausa y posición pertenecen al navegador. `play()` puede rechazarse por política de reproducción. |
| M1 | [SDK Python MCP](https://github.com/modelcontextprotocol/python-sdk), server/transports | Herramientas con stdio y transporte HTTP; verificar versión estable y schemas antes de instalar. |
| M2 | [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) | Autorización de recursos HTTP, validación de audience y prohibición de token passthrough. |

## Decisión propuesta

FastAPI prepara documentos y genera audio; Nuxt reproduce y contiene toda la interfaz y sus controles. El primer motor candidato es Kokoro-ONNX por su enfoque de inferencia, condicionado a una prueba con español. No se elige una voz «mejor» sin escucharla. No se descargaron modelos ni se instaló PyTorch anticipadamente.

El MCP de nuestra app recibe contenido desde agentes y consulta documentos/trabajos. Su adaptador stdio usa rutas de agente con credencial limitada y propietario fijo, y reutiliza servicios de FastAPI. No expone shell ni archivos arbitrarios. El token de servicio es una propuesta personal de alcance acotado; un MCP HTTP externo requeriría su propio diseño de autorización compatible, no copiar esa credencial como solución universal.

No se definen herramientas para pausar/reanudar/reiniciar. Esas acciones ocurren en Nuxt sobre su HTMLAudioElement y no llaman al servidor. La integración Codex/Claude y el flujo de documento enviado están en la [ficha 15](15-conexion-mcp-codex-y-claude.md) y [API 04](../plans/04-api-voz-y-mcp.md).
