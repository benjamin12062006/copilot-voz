import type { AccessState } from '../types/access';

export function useAccess() {
  const state = useState<AccessState>('access', () => ({ status: 'checking' }));
  const { $access } = useNuxtApp();
  return { state: readonly(state), actions: $access };
}
