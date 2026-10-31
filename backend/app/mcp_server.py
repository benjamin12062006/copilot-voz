"""MCP stdio: una sola herramienta; el almacenamiento pertenece a FastAPI."""

import os
from urllib.parse import urlsplit

import httpx
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

if os.environ.get("COPILOT_MCP_ENV_FILE") and os.path.isfile(
    os.environ["COPILOT_MCP_ENV_FILE"]
):
    load_dotenv(os.environ["COPILOT_MCP_ENV_FILE"])

mcp = MCPServer("Copilot Markdown")


@mcp.tool()
async def voice_submit_document(
    title: str, markdown: str, idempotency_key: str
) -> dict:
    """Enviar Markdown a Copilot. Reutilizar la clave al reintentar el mismo envío.

    La clave evita duplicados mientras el documento siga retenido.
    Guarda el documento; no reproduce audio. La API aplica el límite de retención configurado por el usuario en la web.
    """
    env_file = os.environ.get("COPILOT_MCP_ENV_FILE")
    if env_file and os.path.isfile(env_file):
        load_dotenv(env_file, override=True)
    base_url = os.environ.get(
        "COPILOT_API_BASE_URL", "http://127.0.0.1:8000/api/v1"
    ).rstrip("/")
    validate_api_url(base_url)
    token = os.environ["COPILOT_MCP_API_TOKEN"]
    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        response = await client.post(
            base_url + "/agent/documents",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": title,
                "markdown": markdown,
                "idempotencyKey": idempotency_key,
            },
        )
    if response.status_code != 200:
        raise ValueError(f"Copilot rechazó el envío ({response.status_code}).")
    return response.json()


def validate_api_url(value: str) -> None:
    url = urlsplit(value)
    is_local_http = url.scheme == "http" and url.hostname in (
        "localhost",
        "127.0.0.1",
        "::1",
    )
    is_https = url.scheme == "https" and bool(url.hostname)
    has_embedded_credentials = url.username is not None or url.password is not None
    if (
        not (is_local_http or is_https)
        or has_embedded_credentials
        or url.query
        or url.fragment
    ):
        raise ValueError(
            "La API debe usar HTTPS, o HTTP exclusivamente en localhost; sin credenciales en la URL."
        )


if __name__ == "__main__":
    mcp.run(transport="stdio")
