import type { AccessState } from '../types/access';

const ACCESS_PATHS = ['/', '/auth', '/session'];

const WORKSPACE_PATHS = ['/home', '/voice', '/account'];

export const HOME_PATH = '/home';

export function isWorkspacePath(path: string) {
  return WORKSPACE_PATHS.some(
    (base) => path === base || path.startsWith(`${base}/`),
  );
}

export function isGuardedPath(path: string) {
  return ACCESS_PATHS.includes(path) || isWorkspacePath(path);
}

/** Ruta que debe mostrarse para este estado, conservando la actual si ya vale. */
export function accessRoute(state: AccessState, currentPath: string) {
  if (state.status === 'ready') {
    return isWorkspacePath(currentPath) ? currentPath : HOME_PATH;
  }
  if (state.status === 'signedOut' || state.status === 'authenticating') {
    return '/auth';
  }
  // Al recargar /voice/… se queda ahí mientras carga (el layout muestra el
  // progreso); pasar por /session haría perder la ruta pedida.
  if (isLoading(state) && isWorkspacePath(currentPath)) {
    return currentPath;
  }
  return '/session';
}

function isLoading(state: AccessState) {
  return state.status === 'checking' || state.status === 'preparingProfile';
}
