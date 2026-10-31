# Copilot

Biblioteca privada de documentos Markdown y texto, con lectura por voz en el navegador y envío de documentos desde clientes MCP.

- `frontend/`: Nuxt 4, Vue y Clerk.
- `backend/`: FastAPI, Turso/libSQL y Upstash Blob.
- `docs/`: contratos, fuentes y planes del proyecto.

## Desarrollo local

Copiar `frontend/.env.example` a `frontend/.env.local` y `backend/.env.example` a `backend/.env`. Completar los valores localmente.

```sh
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

En otra terminal:

```sh
cd backend
uv sync --locked
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

## Despliegue

Configuración preparada para dos servicios del mismo repositorio:

| Servicio | Directorio | Plataforma |
| --- | --- | --- |
| `copilot-frontend` | `frontend` | Vercel, Nuxt/Nitro y recursos estáticos |
| `copilot-backend` | `backend` | Vercel Functions, FastAPI y Python 3.12 |

Ambos componentes se despliegan mediante GitHub Actions en Vercel, sin Docker ni Containers. Turso y Upstash Blob conservan los datos existentes.

- Frontend: https://copilot-frontend-lovat.vercel.app
- Backend: https://copilot-backend-navy.vercel.app
- [Procedimiento del backend y fuentes consultadas](fonts/deploy/backend/01-procedimiento-fastapi-vercel.md).
- [Procedimiento del frontend](fonts/deploy/frontend/01-procedimiento-nuxt-vercel.md).
- [URLs, variables y CORS entre ambos](fonts/deploy/backend/04-conectar-frontend-y-cors.md).

GitHub Actions valida ambos componentes. El workflow de producción del backend ejecuta sus pruebas, obtiene la configuración de Vercel, compila una vez, despliega esos artefactos y comprueba `/health`.

Los archivos `.env`, `.vercel`, tokens y credenciales se excluyen de Git y del código que se sube a Vercel. Solo se publican plantillas vacías.
