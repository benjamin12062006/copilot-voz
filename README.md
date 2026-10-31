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

## Cloudflare

Configuración preparada para dos servicios del mismo repositorio:

| Servicio | Directorio | Plataforma |
| --- | --- | --- |
| `copilot-frontend` | `frontend` | Workers + recursos estáticos |
| `copilot-backend` | `backend` | Worker + Container Linux |

La [guía de despliegue](docs/deployment/01-cloudflare.md) contiene los comandos exactos, las variables y la conexión con GitHub. El backend usa Containers para conservar su controlador nativo `libsql`; requiere Workers Paid.

GitHub Actions valida ambos componentes y construye/prueba la imagen Docker. El despliegue se realiza mediante la integración nativa Workers Builds cuando se conecte el repositorio en Cloudflare.

Los archivos `.env`, `.dev.vars`, tokens y credenciales se excluyen de Git y de la imagen Docker. Solo se publican plantillas vacías.
