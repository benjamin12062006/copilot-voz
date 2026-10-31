import type { DocumentSummary } from '../types/documents';

type LibraryState =
  | { status: 'loading' }
  | { status: 'ready'; documents: DocumentSummary[] }
  | { status: 'error'; message: string };

// Solo la respuesta más reciente actualiza la lista (refrescos solapados).
let latestRefresh = 0;

/** Lista de documentos compartida por el lateral y las vistas. */
export function useDocumentLibrary() {
  const state = useState<LibraryState>('library', () => ({
    status: 'loading',
  }));
  const owner = useState<string | null>('library-owner', () => null);
  const access = useState<import('../types/access').AccessState>('access');
  const currentOwner = () =>
    access.value.status === 'ready' ? access.value.user.id : null;
  const { $documents } = useNuxtApp();

  const documents = computed(() =>
    state.value.status === 'ready' && owner.value === currentOwner()
      ? state.value.documents
      : [],
  );

  async function refresh() {
    const current = ++latestRefresh;
    const requestedOwner = currentOwner();
    if (!requestedOwner) {
      state.value = { status: 'loading' };
      owner.value = null;
      return;
    }
    if (owner.value !== requestedOwner) state.value = { status: 'loading' };
    owner.value = requestedOwner;
    // Al refrescar con datos ya visibles, se mantienen hasta tener los nuevos.
    if (state.value.status !== 'ready') state.value = { status: 'loading' };

    try {
      const documents = await $documents.list();
      if (current === latestRefresh && requestedOwner === currentOwner()) {
        state.value = { status: 'ready', documents };
      }
    } catch {
      if (
        current === latestRefresh &&
        requestedOwner === currentOwner() &&
        state.value.status !== 'ready'
      ) {
        state.value = {
          status: 'error',
          message: 'No pudimos cargar tus documentos.',
        };
      }
    }
  }

  return { state: readonly(state), documents, refresh };
}
