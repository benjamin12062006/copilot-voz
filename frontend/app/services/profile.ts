import {
  AccessFailure,
  type AppUser,
  type SessionService,
} from '../types/access';

function parseUser(response: unknown): AppUser {
  if (
    typeof response !== 'object' ||
    response === null ||
    !('user' in response)
  ) {
    throw new AccessFailure(
      'La respuesta de tu cuenta no es válida.',
      'configuration',
    );
  }
  const user = response.user;
  if (
    typeof user !== 'object' ||
    user === null ||
    !('id' in user) ||
    typeof user.id !== 'string' ||
    !user.id ||
    !('email' in user) ||
    !(user.email === null || typeof user.email === 'string') ||
    !('displayName' in user) ||
    !(user.displayName === null || typeof user.displayName === 'string') ||
    !('createdAt' in user) ||
    typeof user.createdAt !== 'string' ||
    !Number.isFinite(Date.parse(user.createdAt)) ||
    !('updatedAt' in user) ||
    typeof user.updatedAt !== 'string' ||
    !Number.isFinite(Date.parse(user.updatedAt))
  ) {
    throw new AccessFailure(
      'La respuesta de tu cuenta no es válida.',
      'configuration',
    );
  }
  return {
    id: user.id,
    email: user.email,
    displayName: user.displayName,
    createdAt: user.createdAt,
    updatedAt: user.updatedAt,
  };
}

export function createProfileService(baseUrl: string, session: SessionService) {
  async function request(method: 'GET' | 'PUT'): Promise<AppUser> {
    for (let attempt = 0; attempt < 2; attempt++) {
      const token = await session.token(attempt === 1);
      try {
        const response = await $fetch<unknown>(`${baseUrl}/users/me`, {
          method,
          headers: {
            Accept: 'application/json',
            Authorization: `Bearer ${token}`,
          },
          timeout: 20_000,
          retry: 0,
          redirect: 'error',
          credentials: 'omit',
        });
        return parseUser(response);
      } catch (error) {
        if (error instanceof AccessFailure) throw error;
        const status =
          typeof error === 'object' && error !== null && 'statusCode' in error
            ? error.statusCode
            : undefined;
        if (status === 401 && attempt === 0) continue;
        if (status === 401) {
          throw new AccessFailure(
            'Tu sesión terminó. Vuelve a entrar.',
            'unauthenticated',
          );
        }
        if (status === 404) {
          throw new AccessFailure(
            'Tu perfil todavía no está disponible.',
            'notFound',
          );
        }
        if (status === 403) {
          throw new AccessFailure(
            'No tienes permiso para acceder a esta cuenta.',
            'forbidden',
          );
        }
        throw new AccessFailure(
          'No pudimos conectar con tu cuenta. Inténtalo de nuevo.',
          'network',
        );
      }
    }
    throw new AccessFailure(
      'No pudimos confirmar tu acceso.',
      'unauthenticated',
    );
  }
  return { read: () => request('GET'), provision: () => request('PUT') };
}
