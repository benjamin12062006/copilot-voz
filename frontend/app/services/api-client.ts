import type { SessionService } from '../types/access';

export class ApiFailure extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

export interface ApiClient {
  request<T>(
    path: string,
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE',
    body?: Record<string, unknown>,
  ): Promise<T>;
}

export function createApiClient(
  baseUrl: string,
  session?: SessionService,
): ApiClient {
  async function request<T>(
    path: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    body?: Record<string, unknown>,
  ): Promise<T> {
    if (!session) throw new ApiFailure(401, 'Inicia sesión para continuar.');
    for (let attempt = 0; attempt < 2; attempt++) {
      const token = await session.token(attempt === 1);
      try {
        return await $fetch<T>(baseUrl + path, {
          method,
          body,
          headers: { Authorization: `Bearer ${token}` },
          credentials: 'omit',
          redirect: 'error',
          retry: 0,
          timeout: 30_000,
        });
      } catch (error) {
        const status = responseStatus(error);
        if (status === 401 && attempt === 0) continue;
        throw new ApiFailure(status, failureMessage(status));
      }
    }
    throw new ApiFailure(401, failureMessage(401));
  }
  return { request };
}

function responseStatus(error: unknown): number {
  if (
    typeof error === 'object' &&
    error !== null &&
    'statusCode' in error &&
    typeof error.statusCode === 'number'
  )
    return error.statusCode;
  return 0;
}

function failureMessage(status: number): string {
  if (status === 401) return 'Tu sesión terminó. Vuelve a entrar.';
  if (status === 403) return 'No tienes permiso para esta operación.';
  if (status === 404) return 'El recurso ya no está disponible.';
  if (status === 409)
    return 'El documento cambió. Recárgalo antes de continuar.';
  if (status === 413) return 'El documento supera el tamaño permitido.';
  if (status === 422) return 'Revisa los datos e inténtalo de nuevo.';
  return 'No pudimos conectar con el servidor. Inténtalo de nuevo.';
}
