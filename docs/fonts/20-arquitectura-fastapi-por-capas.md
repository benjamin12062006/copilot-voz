# 20 — FastAPI por capas: estructura por funcionalidad

Fecha de creación: 2026-10-31
Tipo de fuente: transcripciones de curso
Origen: curso «FastAPI Completo» (título en los metadatos: «Pydantic, Bases de datos, SQLAlchemy, SQLModel, JWT, Funciones síncronas y asíncronas, middlewares, alembic y más»). El instructor no consta.
Fecha de consulta: 2026-10-31
Relacionada con: [plan 07](../plans/07-reorganizar-backend-legible.md), [arquitectura y legibilidad](../product/03-arquitectura-y-legibilidad.md), [ficha 16](16-fastapi-base-curso.md)

## Necesidad de consulta

El usuario pidió reorganizar el backend con arquitectura limpia y código legible. Antes de la reorganización, `app/` tenía 15 módulos en una sola carpeta que mezclaban rutas, SQL y reglas.

## Localización verificable

Biblioteca: `/Users/benji/Documents/chrome-extencions/trancripciones/`. Sección: `FastAPI/FastAPI Completo/Sección 7 Arquitectura y modularización del proyecto/`.

| ID | Lección | Líneas |
| --- | --- | --- |
| F1 | `110. Estructura de archivos.md` | 13–31 |
| F2 | `111. Arquitectura de capas.md` | 13–31 |

## Evidencia

- **F1:** pasar de todo en `main.py` a `core/` (base de datos, configuración, excepciones, seguridad) y una carpeta por funcionalidad con `router`, `schemas`, `repository` y `service`, donde el servicio guarda «las reglas de negocio». Las migraciones y los tests quedan fuera. El curso insiste en que «no hay una arquitectura correcta».
- **F2:** el router es el mesero, que toma y valida la orden (DTO de entrada); el repositorio es la cocina, que sabe hacer las consultas. Separar no es por estética: evita archivos enormes, difíciles de probar, y exponer campos que no deberían salir.

## Interpretación y límites

El curso versiona dentro de `api/v1/`. Aquí el prefijo `/api/v1` ya lo pone `main.py`, así que no se añade una carpeta de versión vacía. Tampoco se crea `service.py` donde la regla cabe en el repositorio o en el store; crearlos sería estructura sin función (regla 10 de legibilidad).

## Aplicación

Carpetas `core/`, `identity/`, `users/`, `agent_tokens/` y `documents/`, cada una con rutas, modelos y acceso a datos separados. Detalle en el [plan 07](../plans/07-reorganizar-backend-legible.md).
