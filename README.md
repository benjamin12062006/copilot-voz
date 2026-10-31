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
| `copilot-frontend` | `frontend` | Workers + recursos estáticos |
| `copilot-backend` | `backend` | Vercel Functions, FastAPI y Python 3.12 |

El backend se despliega mediante [GitHub Actions en Vercel](docs/deployment/02-vercel-backend.md), sin Docker ni Containers. Turso y Upstash Blob conservan los datos existentes. El frontend sigue preparado para Cloudflare; su despliegue es una etapa posterior.

GitHub Actions valida ambos componentes. El workflow de producción del backend ejecuta sus pruebas, obtiene la configuración de Vercel, compila una vez, despliega esos artefactos y comprueba `/health`.

Los archivos `.env`, `.vercel`, tokens y credenciales se excluyen de Git y del código que se sube a Vercel. Solo se publican plantillas vacías.
