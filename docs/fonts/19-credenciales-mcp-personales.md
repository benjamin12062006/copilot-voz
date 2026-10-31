# 19 — Credenciales MCP personales

Fecha de creación: 2026-10-31
Tipo de fuente: documentación oficial y código del proyecto
Relacionada con: [plan](../plans/02.1-tokens-mcp-por-usuario.md), [implementación](../../bitacora-construccion/backend/07-tokens-personales-y-textos-por-usuario.md)

- [Python secrets](https://docs.python.org/3/library/secrets.html), Generating tokens: aleatoriedad criptográfica y comparación con compare_digest. Adaptación: 32 bytes aleatorios, credencial opaca, solo hash SHA-256 en Turso; no es una contraseña humana que necesite una función de derivación lenta.
- [OWASP REST Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html), HTTPS / Access Control / JWT: cada ruta valida autenticación y autorización. Adaptación: Clerk solo emite tokens personales para el agente; la credencial del agente solo autoriza enviar Markdown y no sirve como sesión web. El adaptador admite HTTPS remoto y HTTP únicamente en loopback, sin redirecciones.
- [Upstash Writing](https://upstash.com/docs/blob/bucket/writing), conditional writes: ETag protege la biblioteca. Los originales son archivos separados e inmutables por versión; retiro registrado para reintentar limpieza. No se atribuye al proveedor una transacción entre varios objetos.

Consulta: 2026-10-31. Duración de 30 días, permiso documents:submit y disposición textos/userId/fileId son decisiones propias del proyecto para el flujo solicitado.
