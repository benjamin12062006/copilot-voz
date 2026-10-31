# 01 — Contexto y responsabilidades

Fecha de creación: 2026-10-30
Última actualización: 2026-10-30
Estado: Plan
Relacionada con: [arquitectura](../product/03-arquitectura-y-legibilidad.md), [plan MCP](../plans/04-api-voz-y-mcp.md)

Diagrama objetivo; los servicios y el MCP propio todavía no están implementados.

```mermaid
flowchart LR
  Persona[Usuario] --> UI["Nuxt / Vue<br/>Inicio, Voz y biblioteca"]
  UI --> Player["HTMLAudioElement en Nuxt<br/>Reproducir, pausa, continuar, reinicio"]
  UI --> Clerk["Clerk<br/>Inicio y sesión"]
  UI -->|HTTPS + JWT| API["FastAPI<br/>Identidad y casos de uso"]
  Codex[Codex] -->|MCP stdio| MCP["MCP Python propio<br/>Enviar contenido y consultar estado"]
  Claude[Claude Code] -->|MCP stdio| MCP
  MCP -->|HTTP + token limitado| Agent["Rutas de agente<br/>Propietario fijo y scopes"]
  Agent --> Cases[Servicios compartidos]
  API --> Cases
  Cases --> Turso["Turso<br/>Usuarios"]
  Cases --> Blob["Upstash Blob privado<br/>Documentos MD / TXT"]
  Cases --> Prepare["Preparación Markdown<br/>Bloques, texto hablado, avisos"]
  Prepare --> TTS["Motor Python de voz<br/>Genera audio"]
  TTS --> Audio[Artefacto temporal privado]
  Audio --> API
  API -->|Audio autorizado| UI
```

La UI completa y la reproducción viven en Nuxt. Python genera audio y protege datos; MCP permite integrar agentes sin sustituir los controles del navegador. Los plugins Turso y Upstash de Codex son herramientas de desarrollo distintas del MCP de nuestra aplicación.
