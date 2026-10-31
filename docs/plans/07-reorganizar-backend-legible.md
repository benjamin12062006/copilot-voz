# 07 — Reorganizar el backend para leerlo de arriba abajo

Fecha de creación: 2026-10-31
Estado: Plan
Ámbito: backend FastAPI (`backend/app`)
Relacionada con: [fuente por capas](../fonts/20-arquitectura-fastapi-por-capas.md), [arquitectura y legibilidad](../product/03-arquitectura-y-legibilidad.md), [revisión del frontend](frontend/06-revision-legible-frontend.md)
Revisión de referencia: `61cd4af` (tag `v0.3.0`, punto de guardado y oráculo)

## Objetivo

Que cada archivo tenga una responsabilidad y se lea de arriba abajo, sin cambiar ningún comportamiento observable. Se considera terminado cuando:

- los 29 tests pasan sin cambiar ninguna aserción;
- una comparación diferencial entre `v0.3.0` y la versión nueva da las mismas salidas;
- la API arranca de verdad.

## Punto de partida

Quince módulos en `app/`, todos al mismo nivel:

- `agent_tokens.py` y `document_routes.py` mezclan rutas, repositorio y reglas.
- `DocumentStore.save` hace cinco cosas en un solo bucle de 50 líneas.
- `prepare` es un único `while` de 60 líneas.
- `database.py` junta la conexión, el repositorio de usuarios y un comando de consola.

## Contratos que no cambian

- Rutas HTTP, métodos, códigos de estado, cuerpos JSON y cabeceras (`Cache-Control: no-store`, `X-Request-ID`).
- Nombres de `app.state` (`settings`, `authenticator`, `users`, `agent_tokens`, `documents`).
- Puntos de entrada con su misma ruta: `app.main:app` (uvicorn), `python -m app.mcp_server` (Zed, Codex y Claude Code), `python -m app.migrations` y `python -m app.database`.
- SQL, parámetros y orden de los efectos (Blob: escribir archivo → índice → limpieza).
- Mensajes de error y el contrato `{"error": …}`.

## Estructura propuesta

```text
app/
  main.py            composición y lifespan            (entrada HTTP, misma ruta)
  mcp_server.py      herramienta MCP stdio             (entrada, misma ruta)
  migrations.py      migraciones manuales              (entrada, misma ruta)
  database.py        comprobar la conexión a Turso     (entrada, misma ruta)
  core/              settings, errors, request_context, health, turso (conexiones)
  identity/          authenticator (verificar JWT de Clerk), dependencies (identidad actual)
  users/             models, repository (SQL), dependencies, routes
  agent_tokens/      repository (SQL), routes
  documents/         models, store (Blob), preparation (Markdown), preferences (Turso), routes
```

Las dependencias van en una sola dirección: rutas → servicios o repositorios → `core`. `identity` no conoce rutas de otras funcionalidades. `documents` usa `users` (propietario) y `agent_tokens` (envío del agente).

## Incrementos

1. Mover a `core/` los módulos transversales y actualizar los imports. Solo cambian rutas de import.
2. `users/` e `identity/`: separar modelos, SQL, dependencias y rutas. La dependencia «id del usuario actual» queda en un solo sitio (hoy está copiada en tres rutas).
3. `agent_tokens/`: repositorio y rutas por separado. Las filas se convierten a JSON con funciones con nombre.
4. `documents/`:
   - `save` orquesta pasos con nombre;
   - el patrón «cargar índice → cambiar → confirmar con etag → reintentar» se nombra una sola vez;
   - `prepare` pasa a una función por tipo de bloque.
5. Mantener los cuatro puntos de entrada en su ruta, más finos, y ordenar `migrations.py` (esquemas esperados como datos con nombre).
6. Actualizar los imports y los destinos de `patch` de los tests, sin tocar ninguna aserción.

## Comprobación prevista

- Los 29 tests de `unittest`.
- Comparación diferencial `v0.3.0` frente a la versión nueva para:
  - `prepare` (muchos Markdown);
  - `DocumentStore` (secuencias de operaciones contra un bucket en memoria);
  - `SessionAuthenticator` y las rutas HTTP (TestClient con dependencias falsas).
- Un cambio forzado para comprobar que la comparación detecta diferencias.
- Arranque real con uvicorn y `GET /health`.
- Las mismas rutas en `openapi.json`.
