import { useAuth } from '@clerk/nuxt/composables';
import { createAccessController } from '../services/access-controller';
import { createProfileService } from '../services/profile';
import {
  AccessFailure,
  type AccessState,
  type SessionService,
} from '../types/access';
import { configurationProblem } from '../utils/configuration';
import { accessRoute } from '../utils/access-route';

export default defineNuxtPlugin({
  name: 'copilot-access',
  enforce: 'post',
  setup() {
    const config = useRuntimeConfig().public;
    const state = useState<AccessState>('access', () => ({
      status: 'checking',
    }));
    const router = useRouter();
    const problem = configurationProblem(config);
    const auth = problem ? undefined : useAuth();

    async function waitForClerk() {
      if (!auth || auth.isLoaded.value) return;
      await new Promise<void>((resolve, reject) => {
        const stop = watch(auth.isLoaded, (loaded) => {
          if (!loaded) return;
          clearTimeout(timer);
          stop();
          resolve();
        });
        const timer = setTimeout(() => {
          stop();
          reject(
            new AccessFailure(
              'No pudimos cargar el acceso. Inténtalo de nuevo.',
              'network',
            ),
          );
        }, 20_000);
      });
    }

    const session: SessionService | undefined = auth
      ? {
          async restore() {
            await waitForClerk();
            return Boolean(auth.isSignedIn.value);
          },
          async token(forceRefresh = false) {
            await waitForClerk();
            const token = await auth.getToken.value({
              skipCache: forceRefresh,
            });
            if (!token)
              throw new AccessFailure(
                'Tu sesión terminó. Vuelve a entrar.',
                'unauthenticated',
              );
            return token;
          },
          async signOut() {
            await auth.signOut.value();
          },
        }
      : undefined;

    const access = createAccessController({
      state,
      session,
      profiles: session
        ? createProfileService(config.apiBaseUrl, session)
        : undefined,
      configurationProblem: problem,
    });

    onNuxtReady(() => {
      const stopNavigation = watch(
        state,
        (value) => {
          if (value.status === 'checking') return;
          const path = accessRoute(value);
          if (router.currentRoute.value.path !== path)
            void router.replace(path);
        },
        { immediate: true },
      );
      const stopSession = auth
        ? watch([auth.isLoaded, auth.isSignedIn], ([loaded, signedIn]) => {
            if (!loaded) return;
            if (
              signedIn &&
              ['signedOut', 'authenticating'].includes(state.value.status)
            ) {
              // The SDK reports both popup/hash login and restored sessions.
              void access.restore();
            } else if (!signedIn && state.value.status === 'ready') {
              void access.signOut();
            }
          })
        : undefined;
      void access.start();
      if (import.meta.hot)
        import.meta.hot.dispose(() => {
          stopNavigation();
          stopSession?.();
        });
    });
    return { provide: { access } };
  },
});
