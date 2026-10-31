import {
  AccessFailure,
  type AppUser,
  type ProfileService,
} from '../../types/access';
import { simulateLatency } from './latency';

export interface SimulatedIdentity {
  id: string;
  email: string | null;
  displayName: string | null;
  createdAt: string;
}

/**
 * Sustituto de GET/PUT /users/me (API 02). Devuelve la misma forma `AppUser`
 * a partir de la identidad que ya conoce el navegador.
 */
export function createSimulatedProfileService(
  readIdentity: () => SimulatedIdentity | null,
): ProfileService {
  async function currentUser(): Promise<AppUser> {
    await simulateLatency(400);
    const identity = readIdentity();
    if (!identity) {
      throw new AccessFailure(
        'Tu sesión terminó. Vuelve a entrar.',
        'unauthenticated',
      );
    }
    return {
      id: `local-${identity.id}`,
      email: identity.email,
      displayName: identity.displayName,
      createdAt: identity.createdAt,
      updatedAt: new Date().toISOString(),
    };
  }

  return { read: currentUser, provision: currentUser };
}
