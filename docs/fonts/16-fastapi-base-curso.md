# 16 — FastAPI Completo: configuración, lifespan, CORS y request ID

Fecha de creación: 2026-10-30
Tipo de fuente: transcripciones de curso
Origen: curso «FastAPI Completo» (título en metadatos: «Pydantic, Bases de datos, SQLAlchemy, SQLModel, JWT, Funciones síncronas y asíncronas, middlewares, alembic y más»). Instructor: no consta en las transcripciones.
Fecha de consulta: 2026-10-30
Relacionada con: [plan API 01](../plans/01-api-base-y-configuracion.md), [bitácora 04](../../bitacora-construccion/backend/04-api-base-y-configuracion.md)

## Necesidad de consulta

API 01 necesitaba un mecanismo fundado para cargar configuración, componer `main.py` con ciclo de vida, configurar CORS para Nuxt e identificar cada petición. Ninguna ficha previa cubría FastAPI.

## Localización verificable

Biblioteca: `/Users/benji/Documents/chrome-extencions/trancripciones/`. Líneas verificadas con `nl -ba`.

| ID | Lección y ruta relativa a la biblioteca | Líneas |
| --- | --- | --- |
| F1 | 236. Archivo de configuración y variables de entorno — `FastAPI/FastAPI Completo/Sección 16 SQLModel - Modelos y Schemas - Devinote/236. Archivo de configuración y variables de entorno.md` | 13–25 |
| F2 | 271. Configurando main.py — `FastAPI/FastAPI Completo/Sección 17 SQLModel - Servicios y rutas - Devinote/271. Configurando main.py.md` | 17–31 |
| F3 | 223. Middleware - Generando Request ID — `FastAPI/FastAPI Completo/Sección 15 Middlewares/223. Middleware - Generando Request ID.md` | 13–21 |
| F4 | 226. Middleware - CORS — `FastAPI/FastAPI Completo/Sección 15 Middlewares/226. Middleware - CORS.md` | 13–39 |

## Evidencia

- **F1:** clase `Settings` de pydantic-settings con campos requeridos (`Field(...)`) y opcionales con valor por defecto; el archivo `.env` se declara en la configuración de la clase y se crea una instancia `settings`.
- **F2:** `main.py` crea `FastAPI`, añade `CORSMiddleware`, monta routers con prefijo `/api/v1` y registra un `lifespan` con `@asynccontextmanager`: «todo lo que esté antes de yield se va a ejecutar cuando la app arranca». En la clase se usan orígenes, métodos y cabeceras `*` por estar en desarrollo, y se llama `load_dotenv` «por si acaso».
- **F3:** middleware HTTP que genera un `uuid4`, espera `call_next` y escribe el ID en una cabecera de respuesta. Uso: si una petición falla, «le podemos pedir el ID y nos lo copia».
- **F4:** CORS responde preflights y autoriza o bloquea orígenes. `*` se presenta como válido solo en desarrollo; para producción «hay que poner aquí el listado de los de los orígenes».

## Interpretación y límites

Las lecciones respaldan el mecanismo (Settings tipado, lifespan, CORS por middleware, ID por petición). No tratan: ocultar valores en errores de configuración, contrato JSON de errores, interacción entre el orden de middlewares y las respuestas 500, ni límites de confianza de un ID enviado por el cliente. Esas partes son propuesta propia. Las APIs se contrastaron con los paquetes instalados (FastAPI 0.162.0, Starlette 1.10.0, pydantic-settings 2.16.2), no con documentación web.

## Aplicación en el proyecto

- F1 → [settings.py](../../backend/app/settings.py) `Settings`/`load_settings`. Adaptación: las variables de funcionalidades futuras son opcionales al arrancar y se exigen con `Settings.require`; `.env` se pasa explícitamente al construir en lugar de `load_dotenv`.
- F2 → [main.py](../../backend/app/main.py) `create_app`/`lifespan`, constante `API_V1_PREFIX`. Adaptación: orígenes, métodos y cabeceras concretos desde el primer día; sin credenciales de cookies.
- F3 → [request_context.py](../../backend/app/request_context.py) `track_request`. Adaptación: el ID también viaja en el cuerpo de error, se expone por CORS y se registra en el log.
- F4 → `allow_frontend_origins` en `main.py`. Adaptación: origen exacto validado al cargar configuración; `*` rechazado.
