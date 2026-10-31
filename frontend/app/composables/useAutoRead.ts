/**
 * Lectura automática: cuando llega un documento nuevo a la biblioteca, se lee
 * en voz alta sin abrirlo, también con la pestaña en segundo plano.
 *
 * Solo funciona mientras la pestaña siga abierta: la voz es la del navegador.
 * La opción es de la cuenta y se guarda en Turso a través de la API.
 */
import { prepareReading } from '../services/reading/prepare-reading';
import type { AccessState } from '../types/access';
import type { DocumentSummary } from '../types/documents';
import type { AutoReadMode } from '../types/voice';

/** Cada cuánto se pregunta a la API si hay documentos nuevos. */
const POLL_INTERVAL_MS = 20_000;

/** Nombre del candado que elige una sola pestaña lectora por navegador. */
const READER_LOCK = 'copilot-auto-read';

/** Estados de la voz en los que se puede empezar otro documento. */
const FREE_VOICE_STATUSES = ['idle', 'ended', 'error', 'unsupported'];

/** La opción elegida en Perfil, compartida con el lector. */
export function useAutoReadMode() {
  const mode = modeState();
  const { $account } = useNuxtApp();

  /** Lee la opción de la cuenta. Si no se puede, queda apagada: nunca habla por sorpresa. */
  async function load() {
    try {
      mode.value = (await $account.voicePreferences()).autoReadMode;
    } catch {
      mode.value = 'off';
    }
  }

  /** Cambia la opción al momento y la guarda; si falla, vuelve a la anterior. */
  async function setMode(next: AutoReadMode) {
    const previous = mode.value;
    mode.value = next;
    try {
      await $account.setAutoReadMode(next);
    } catch (error) {
      mode.value = previous;
      throw error;
    }
  }

  return { mode: readonly(mode), load, setMode };
}

/**
 * Vigila la biblioteca y lee lo que llega. Se usa una sola vez, en el layout
 * del espacio de trabajo, para que siga activo al cambiar de página.
 */
export function useAutoReader() {
  const mode = modeState();
  const { load: loadMode } = useAutoReadMode();
  const access = useState<AccessState>('access');
  const library = useDocumentLibrary();
  const { $documents, $voice } = useNuxtApp();
  const toast = useToast();

  const queue: DocumentSummary[] = [];
  // null hasta ver la primera lista completa: lo que ya había no se lee.
  let knownIds: Set<string> | null = null;
  let pollTimer: ReturnType<typeof setInterval> | undefined;
  let isReaderTab = false;
  let releaseReaderLock: (() => void) | null = null;
  let isPreparingNext = false;
  let hasAskedForClick = false;

  const isEnabled = computed(() => mode.value !== 'off');
  const userId = computed(() =>
    access.value.status === 'ready' ? access.value.user.id : null,
  );

  watch(isEnabled, (enabled) => (enabled ? start() : stop()));
  watch(library.documents, enqueueNewDocuments);
  watch(() => $voice.state.value.status, readNextWhenFree);

  onMounted(() => {
    // Solo en el navegador (la API se llama desde aquí): al entrar y al cambiar de cuenta.
    watch(userId, loadModeFor, { immediate: true });
    // Tras recargar, el navegador no deja hablar hasta el primer clic.
    window.addEventListener('pointerdown', readNextWhenFree);
  });

  onBeforeUnmount(() => {
    stop();
    window.removeEventListener('pointerdown', readNextWhenFree);
  });

  function loadModeFor(id: string | null) {
    if (id) void loadMode();
    else mode.value = 'off';
  }

  function start() {
    knownIds = null;
    enqueueNewDocuments(library.documents.value);
    pollTimer = setInterval(() => void library.refresh(), POLL_INTERVAL_MS);
    void becomeReaderTab();
  }

  function stop() {
    clearInterval(pollTimer);
    queue.length = 0;
    knownIds = null;
    isReaderTab = false;
    releaseReaderLock?.();
    releaseReaderLock = null;
  }

  function enqueueNewDocuments(documents: readonly DocumentSummary[]) {
    if (!isEnabled.value || library.state.value.status !== 'ready') return;

    if (knownIds === null) {
      knownIds = new Set(documents.map((document) => document.id));
      return;
    }

    const known = knownIds;
    const arrivals = documents
      .filter((document) => !known.has(document.id))
      .sort(byOldestFirst);
    for (const document of arrivals) known.add(document.id);

    queue.push(...arrivals.filter(matchesMode));
    void readNextWhenFree();
  }

  async function readNextWhenFree() {
    if (!canStartNext()) return;
    if (!hasUserActivation()) {
      askForClickOnce();
      return;
    }

    const next = queue.shift();
    if (!next) return;

    isPreparingNext = true;
    const document = await fetchDocument(next.id);
    isPreparingNext = false;

    // Se borró antes de leerlo, o se apagó la opción mientras se pedía.
    if (!document || !isEnabled.value) {
      void readNextWhenFree();
      return;
    }

    const prepared = prepareReading(document.format, document.content);
    void $voice.read(document.id, document.title, prepared);
    toast.add({
      title: `Leyendo «${document.title}»`,
      icon: 'i-lucide-audio-lines',
      actions: [{ label: 'Abrir', to: `/voice/${document.id}` }],
    });
  }

  async function fetchDocument(id: string) {
    try {
      return await $documents.get(id);
    } catch {
      return null;
    }
  }

  /**
   * Con varias pestañas abiertas solo lee la primera; las demás esperan el
   * candado y toman el relevo si esa se cierra.
   */
  async function becomeReaderTab() {
    if (!('locks' in navigator)) {
      isReaderTab = true;
      return;
    }
    await navigator.locks.request(READER_LOCK, () => {
      // Se pudo apagar la opción mientras esta pestaña esperaba su turno.
      if (!isEnabled.value) return;
      isReaderTab = true;
      void readNextWhenFree();
      return new Promise<void>((release) => {
        releaseReaderLock = release;
      });
    });
  }

  function canStartNext() {
    const isVoiceFree = FREE_VOICE_STATUSES.includes($voice.state.value.status);
    return (
      isEnabled.value &&
      isReaderTab &&
      queue.length > 0 &&
      isVoiceFree &&
      !isPreparingNext
    );
  }

  function matchesMode(document: DocumentSummary) {
    return mode.value === 'all' || document.origin === 'agent';
  }

  function askForClickOnce() {
    if (hasAskedForClick) return;
    hasAskedForClick = true;
    toast.add({
      title: 'Ha llegado un documento nuevo',
      description: 'Haz clic en la página para que pueda leerlo en voz alta.',
      icon: 'i-lucide-hand',
    });
  }
}

function modeState() {
  return useState<AutoReadMode>('auto-read-mode', () => 'off');
}

/**
 * Chrome y Safari solo hablan si la persona ya tocó la página alguna vez.
 * Si el navegador no lo informa, se intenta igualmente.
 */
function hasUserActivation() {
  return navigator.userActivation?.hasBeenActive ?? true;
}

function byOldestFirst(a: DocumentSummary, b: DocumentSummary) {
  return a.updatedAt.localeCompare(b.updatedAt);
}
