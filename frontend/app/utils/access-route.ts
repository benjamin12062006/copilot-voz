import type { AccessState } from '../types/access';

export function accessRoute(state: AccessState) {
  if (state.status === 'ready') return '/account';
  if (state.status === 'signedOut' || state.status === 'authenticating')
    return '/auth';
  return '/session';
}
