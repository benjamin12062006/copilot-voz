import { useAuth, useUser } from '@clerk/nuxt/composables';
import type { Ref } from 'vue';
import {
  createAccessController,
  type AccessController,
} from '../services/access-controller';
import {
  createSimulatedProfileService,
  type SimulatedIdentity,
} from '../services/mock/profile';
import { createPreviewSession } from '../services/preview-session';
import { createProfileService } from '../services/profile';
import {
  AccessFailure,
  type AccessState,
  type ProfileService,
  type SessionService,
} from '../types/access';
import { accessRoute } from '../utils/access-route';
import { configurationProblem } from '../utils/configuration';

type PublicConfig = ReturnType<typeof useRuntimeConfig>['public'];

/** Qué proveedor de sesión está activo; los componentes de Clerk solo existen con 'clerk'. */
export type AccessProvider = 'clerk' | 'preview' | 'none';

const CLERK_LOAD_TIMEOUT_MS = 20_000;

export default defineNuxtPlugin({
  name: 'copilot-access',
  enforce: 'post',
  setup(): {
    provide: {
      access: AccessController;
      accessProvider: AccessProvider;
      session: SessionService | undefined;
    };
  } {
    const config = useRuntimeConfig().public;
    const state = useState<AccessState>('access', () => ({
      status: 'checking',
    }));

    // `import.meta.dev` elimina la vista previa del build de producción.
    const preview =
      import.meta.dev && config.previewSession
        ? createPreviewSession()
        : undefined;
    const problem = preview ? undefined : configurationProblem(config);
    const clerk = preview || problem ? undefined : connectClerk();

    const session = preview?.session ?? clerk?.session;
    const identity = preview?.identity ?? clerk?.identity ?? (() => null);

    const access = createAccessController({
      state,
      session,
      profiles: session
        ? chooseProfiles(config, session, identity, Boolean(preview))
        : undefined,
      configurationProblem: problem,
    });

    const router = useRouter();

    function followSignIn() {
      if (clerk) return clerk.followSignIn(state, access);
      if (preview) return followPreviewSignIn(state, access, preview.signIn);
      return undefined;
    }

    onNuxtReady(() => {
      const stopNavigation = followAccessState(state, router);
      const stopSignIn = followSignIn();

      void access.start();

      if (import.meta.hot) {
        import.meta.hot.dispose(() => {
          stopNavigation();
          stopSignIn?.();
        });
      }
    });

    let accessProvider: AccessProvider = 'none';
    if (preview) accessProvider = 'preview';
    if (clerk) accessProvider = 'clerk';

    return { provide: { access, accessProvider, session } };
  },
});

/** Con `dataSource: 'mock'` el perfil se simula hasta que exista API 02. */
function chooseProfiles(
  config: PublicConfig,
  session: SessionService,
  identity: () => SimulatedIdentity | null,
  preview: boolean,
): ProfileService {
  if (config.dataSource === 'api' && !preview) {
    const profiles = createProfileService(config.apiBaseUrl, session);
    const displayDetails = (
      user: Awaited<ReturnType<ProfileService['read']>>,
    ) => ({
      ...user,
      email: user.email ?? identity()?.email ?? null,
      displayName: user.displayName ?? identity()?.displayName ?? null,
    });
    return {
      read: async () => displayDetails(await profiles.read()),
      provision: async () => displayDetails(await profiles.provision()),
    };
  }
  return createSimulatedProfileService(identity);
}

function connectClerk() {
  const auth = useAuth();
  const { user } = useUser();

  async function waitForClerk() {
    if (auth.isLoaded.value) return;
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
      }, CLERK_LOAD_TIMEOUT_MS);
    });
  }

  const session: SessionService = {
    async restore() {
      await waitForClerk();
      return Boolean(auth.isSignedIn.value);
    },
    async token(forceRefresh = false) {
      await waitForClerk();
      const token = await auth.getToken.value({ skipCache: forceRefresh });
      if (!token) {
        throw new AccessFailure(
          'Tu sesión terminó. Vuelve a entrar.',
          'unauthenticated',
        );
      }
      return token;
    },
    async signOut() {
      await auth.signOut.value();
    },
  };

  function identity(): SimulatedIdentity | null {
    const current = user.value;
    if (!current) return null;
    return {
      id: current.id,
      email: current.primaryEmailAddress?.emailAddress ?? null,
      displayName: current.fullName || current.username || null,
      createdAt: (current.createdAt ?? new Date()).toISOString(),
    };
  }

  function followSignIn(state: Ref<AccessState>, access: AccessController) {
    return watch([auth.isLoaded, auth.isSignedIn], ([loaded, signedIn]) => {
      if (!loaded) return;
      const waitingForSignIn = ['signedOut', 'authenticating'].includes(
        state.value.status,
      );
      if (signedIn && waitingForSignIn) {
        // El SDK avisa tanto del login recién hecho como de la sesión restaurada.
        void access.restore();
      } else if (!signedIn && state.value.status === 'ready') {
        void access.signOut();
      }
    });
  }

  return { session, identity, followSignIn };
}

function followPreviewSignIn(
  state: Ref<AccessState>,
  access: AccessController,
  signIn: () => void,
) {
  return watch(
    () => state.value.status,
    (status) => {
      if (status !== 'authenticating') return;
      signIn();
      void access.restore();
    },
  );
}

/** Lleva a la ruta que corresponde al estado de acceso. Solo navega: la API autoriza. */
function followAccessState(
  state: Ref<AccessState>,
  router: ReturnType<typeof useRouter>,
) {
  return watch(
    state,
    (value) => {
      if (value.status === 'checking') return;
      const currentPath = router.currentRoute.value.path;
      const destination = accessRoute(value, currentPath);
      if (currentPath !== destination) void router.replace(destination);
    },
    { immediate: true },
  );
}
