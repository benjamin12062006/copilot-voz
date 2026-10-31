import type { SessionService } from '../types/access';
import type { SimulatedIdentity } from './mock/profile';

export const PREVIEW_IDENTITY: SimulatedIdentity = {
  id: 'vista-previa',
  email: 'vista.previa@copilot.local',
  displayName: 'Vista previa',
  createdAt: '2026-10-01T12:00:00.000Z',
};

/**
 * Sesión falsa para revisar el diseño sin Clerk (`pnpm dev:preview`).
 * El plugin solo la usa con `import.meta.dev`, así que no llega a producción.
 */
export function createPreviewSession() {
  let signedIn = true;

  const session: SessionService = {
    async restore() {
      return signedIn;
    },
    async token() {
      return 'vista-previa';
    },
    async signOut() {
      signedIn = false;
    },
  };

  function signIn() {
    signedIn = true;
  }

  function identity() {
    return signedIn ? PREVIEW_IDENTITY : null;
  }

  return { session, signIn, identity };
}
