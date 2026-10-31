import { Container, getContainer } from '@cloudflare/containers';

interface Env {
  COPILOT_API: DurableObjectNamespace<CopilotApi>;
  COPILOT_ENV: string;
  COPILOT_CORS_ORIGINS: string;
  COPILOT_STORAGE_NAMESPACE: string;
  COPILOT_STORAGE_MAX_DOCUMENT_BYTES?: string;
  COPILOT_ALLOWED_CLERK_USER_IDS?: string;
  CLERK_ISSUER: string;
  CLERK_AUTHORIZED_PARTIES?: string;
  CLERK_JWT_KEY?: string;
  CLERK_SECRET_KEY?: string;
  TURSO_DATABASE_URL: string;
  TURSO_AUTH_TOKEN: string;
  UPSTASH_BLOB_TOKEN: string;
}

export class CopilotApi extends Container<Env> {
  defaultPort = 8000;
  sleepAfter = '2m';
  enableInternet = true;
  envVars = containerEnvironment(this.env);
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Un nombre fijo limita la aplicación inicial a una instancia compartida.
    // La autenticación y la separación de usuarios siguen dentro de FastAPI.
    return getContainer(env.COPILOT_API, 'api').fetch(request);
  },
} satisfies ExportedHandler<Env>;

function containerEnvironment(env: Env): Record<string, string> {
  const values: Record<string, string | undefined> = {
    COPILOT_ENV: env.COPILOT_ENV,
    COPILOT_CORS_ORIGINS: env.COPILOT_CORS_ORIGINS,
    COPILOT_STORAGE_NAMESPACE: env.COPILOT_STORAGE_NAMESPACE,
    COPILOT_STORAGE_MAX_DOCUMENT_BYTES: env.COPILOT_STORAGE_MAX_DOCUMENT_BYTES,
    COPILOT_ALLOWED_CLERK_USER_IDS: env.COPILOT_ALLOWED_CLERK_USER_IDS,
    CLERK_ISSUER: env.CLERK_ISSUER,
    CLERK_AUTHORIZED_PARTIES: env.CLERK_AUTHORIZED_PARTIES,
    CLERK_JWT_KEY: env.CLERK_JWT_KEY,
    CLERK_SECRET_KEY: env.CLERK_SECRET_KEY,
    TURSO_DATABASE_URL: env.TURSO_DATABASE_URL,
    TURSO_AUTH_TOKEN: env.TURSO_AUTH_TOKEN,
    UPSTASH_BLOB_TOKEN: env.UPSTASH_BLOB_TOKEN,
    UPSTASH_DISABLE_TELEMETRY: 'true',
  };

  const configured: Record<string, string> = {};
  for (const [name, value] of Object.entries(values)) {
    if (value) configured[name] = value;
  }
  return configured;
}
