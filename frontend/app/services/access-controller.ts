import type { Ref } from 'vue';
import {
  AccessFailure,
  type AccessState,
  type AccessStage,
  type ProfileService,
  type SessionService,
} from '../types/access';

interface AccessDependencies {
  state: Ref<AccessState>;
  session?: SessionService;
  profiles?: ProfileService;
  configurationProblem?: string;
}

/** One controller per Nuxt app. Generations discard work from cancelled attempts. */
export function createAccessController({
  state,
  session,
  profiles,
  configurationProblem,
}: AccessDependencies) {
  let generation = 0;
  let started = false;
  let restoring: Promise<void> | undefined;
  let provision = false;

  const current = (attempt: number) => attempt === generation;

  async function failed(error: unknown, stage: AccessStage, attempt: number) {
    if (!current(attempt)) return;
    if (error instanceof AccessFailure && error.kind === 'unauthenticated') {
      await signOut();
      return;
    }
    state.value = {
      status: 'error',
      stage,
      message:
        error instanceof AccessFailure
          ? error.message
          : 'Algo interrumpió la conexión. Inténtalo de nuevo.',
    };
  }

  async function prepare(attempt: number) {
    if (!current(attempt) || !profiles) return;
    state.value = { status: 'preparingProfile' };
    try {
      let user;
      if (provision) {
        user = await profiles.provision();
      } else {
        try {
          user = await profiles.read();
        } catch (error) {
          if (!(error instanceof AccessFailure) || error.kind !== 'notFound')
            throw error;
          if (!current(attempt)) return;
          user = await profiles.provision();
        }
      }
      if (current(attempt)) state.value = { status: 'ready', user };
    } catch (error) {
      await failed(error, 'profile', attempt);
    }
  }

  async function restore() {
    const attempt = ++generation;
    if (configurationProblem || !session || !profiles) {
      state.value = {
        status: 'error',
        stage: 'configuration',
        message:
          configurationProblem ||
          'El acceso todavía no está configurado en este entorno.',
      };
      return;
    }
    state.value = { status: 'checking' };
    try {
      const authenticated = await session.restore();
      if (!current(attempt)) return;
      if (!authenticated) {
        state.value = { status: 'signedOut' };
        return;
      }
      provision = false;
      await prepare(attempt);
    } catch (error) {
      await failed(error, 'restore', attempt);
    }
  }

  async function start() {
    if (restoring) return restoring;
    if (started) return;
    started = true;
    restoring = restore();
    try {
      await restoring;
    } finally {
      restoring = undefined;
    }
  }

  function beginSignIn() {
    if (state.value.status !== 'signedOut') return;
    state.value = { status: 'authenticating', attempt: ++generation };
  }

  function cancelSignIn() {
    if (state.value.status !== 'authenticating') return;
    generation++;
    state.value = { status: 'signedOut' };
  }

  async function completeSignIn(attempt: number) {
    if (!current(attempt) || state.value.status !== 'authenticating') return;
    provision = true;
    await prepare(attempt);
  }

  function failSignIn(attempt: number) {
    if (!current(attempt) || state.value.status !== 'authenticating') return;
    state.value = {
      status: 'error',
      stage: 'login',
      message: 'No pudimos cargar el acceso. Inténtalo de nuevo.',
    };
  }

  async function signOut() {
    if (state.value.status === 'signingOut') return;
    const attempt = ++generation;
    state.value = { status: 'signingOut' };
    try {
      await session?.signOut();
    } catch {
      if (current(attempt)) {
        state.value = {
          status: 'error',
          stage: 'logout',
          message:
            'No pudimos cerrar tu sesión. Puede seguir activa; inténtalo de nuevo.',
        };
      }
      return;
    }
    if (current(attempt)) state.value = { status: 'signedOut' };
  }

  async function retry() {
    if (state.value.status !== 'error') return;
    const { stage } = state.value;
    if (stage === 'logout') {
      await signOut();
    } else if (stage === 'login') {
      state.value = { status: 'signedOut' };
    } else if (stage === 'profile') {
      await prepare(++generation);
    } else {
      await restore();
    }
  }

  return {
    start,
    restore,
    beginSignIn,
    cancelSignIn,
    completeSignIn,
    failSignIn,
    signOut,
    retry,
  };
}

export type AccessController = ReturnType<typeof createAccessController>;
