<script setup lang="ts">
import { prepareReading } from '../../services/reading/prepare-reading';
import {
  DocumentFailure,
  type DocumentDraft,
  type VoiceDocument,
} from '../../types/documents';

definePageMeta({ layout: 'workspace' });

const route = useRoute();
const { $documents, $voice } = useNuxtApp();
const library = useDocumentLibrary();
const toast = useToast();

const VIEW_TABS = [
  { label: 'Lectura', value: 'reading', icon: 'i-lucide-book-open' },
  { label: 'Original', value: 'original', icon: 'i-lucide-file-code-2' },
];

const document = ref<VoiceDocument | null>(null);
const loading = ref(true);
const loadError = ref<string | null>(null);
const view = ref('reading');

const editing = ref(false);
const deleting = ref(false);
const draft = ref<DocumentDraft>({
  title: '',
  format: 'markdown',
  content: '',
});
const saving = ref(false);
const saveError = ref<string | null>(null);
const hasConflict = ref(false);

// Cada carga invalida la anterior: una respuesta tardía no pisa el documento actual.
let latestLoad = 0;

// Se prepara aquí mismo y al instante: cambia solo si cambia el documento.
const prepared = computed(() =>
  document.value
    ? prepareReading(document.value.format, document.value.content)
    : null,
);

/** Primera frase de cada bloque que se lee, para «Leer desde aquí». */
const firstSegmentOfBlock = computed(() => {
  const firstSegments = new Map<number, number>();
  prepared.value?.segments.forEach((segment, index) => {
    if (!firstSegments.has(segment.blockIndex)) {
      firstSegments.set(segment.blockIndex, index);
    }
  });
  return firstSegments;
});

const isReadingThis = computed(
  () =>
    document.value !== null &&
    $voice.state.value.documentId === document.value.id,
);
const activeBlock = computed(() =>
  isReadingThis.value ? $voice.state.value.blockIndex : null,
);
const canListen = computed(() => Boolean(prepared.value?.segments.length));
const hasUnsavedEdits = computed(
  () =>
    editing.value && document.value !== null && draftDiffers(document.value),
);
const meta = computed(() => {
  if (!document.value) return '';
  return [
    FORMAT_LABELS[document.value.format],
    `${document.value.wordCount} palabras`,
    `actualizado ${formatRelativeDate(document.value.updatedAt)}`,
  ].join(' · ');
});

watch(
  () => route.params.id,
  (id) => {
    if (typeof id === 'string') void loadDocument(id);
  },
  { immediate: true },
);

async function loadDocument(id: string) {
  const current = ++latestLoad;
  // Abrir el documento que ya está sonando (p. ej. por lectura automática) no lo corta.
  if ($voice.state.value.documentId !== id) $voice.stop();
  editing.value = false;
  loading.value = true;
  loadError.value = null;

  const loaded = await fetchDocument(id);
  if (current !== latestLoad) return;
  document.value = loaded;
  loading.value = false;
}

async function fetchDocument(id: string) {
  try {
    return await $documents.get(id);
  } catch (error) {
    loadError.value =
      error instanceof DocumentFailure
        ? error.message
        : 'No pudimos abrir el documento.';
    return null;
  }
}

/** Lee en voz alta desde el principio o desde una frase concreta. */
function listen(fromSegment = 0) {
  if (!prepared.value || !document.value) return;
  if (isReadingThis.value && fromSegment > 0) {
    $voice.jumpTo(fromSegment);
    return;
  }
  // Pulsar el botón es la acción del usuario que el navegador exige para hablar.
  void $voice.read(
    document.value.id,
    document.value.title,
    prepared.value,
    fromSegment,
  );
}

async function deleteDocument() {
  const current = document.value;
  if (
    !current ||
    !window.confirm(
      `¿Eliminar «${current.title}»? Se borrará de tu biblioteca.`,
    )
  )
    return;
  deleting.value = true;
  $voice.stop();
  try {
    await $documents.remove(current.id, current.revision);
    document.value = null;
    await library.refresh();
    await navigateTo('/voice');
    toast.add({ title: 'Documento eliminado', color: 'success' });
  } catch (error) {
    toast.add({
      title:
        error instanceof Error
          ? error.message
          : 'No pudimos eliminar el documento.',
      color: 'error',
    });
  } finally {
    deleting.value = false;
  }
}

function startEditing() {
  if (!document.value) return;
  const { title, format, content } = document.value;
  draft.value = { title, format, content };
  saveError.value = null;
  hasConflict.value = false;
  editing.value = true;
}

function cancelEditing() {
  if (hasUnsavedEdits.value && !confirmDiscard()) return;
  editing.value = false;
}

async function saveEdits() {
  if (!document.value) return;
  saving.value = true;
  saveError.value = null;
  const updated = await updateDocument(document.value);
  saving.value = false;
  if (!updated) return;

  // El texto cambió: la lectura en curso ya no corresponde a lo que se ve.
  $voice.stop();
  document.value = updated;
  editing.value = false;
  toast.add({
    title: 'Cambios guardados',
    icon: 'i-lucide-check',
    color: 'success',
  });
  void library.refresh();
}

/** Si falla, el borrador queda intacto en el editor. */
async function updateDocument(current: VoiceDocument) {
  try {
    return await $documents.update(current.id, draft.value, current.revision);
  } catch (error) {
    hasConflict.value =
      error instanceof DocumentFailure && error.kind === 'conflict';
    saveError.value =
      error instanceof DocumentFailure
        ? error.message
        : 'No pudimos guardar. Tu borrador sigue aquí.';
    return null;
  }
}

async function discardAndReload() {
  if (!confirmDiscard()) return;
  editing.value = false;
  const id = route.params.id;
  if (typeof id === 'string') await loadDocument(id);
}

function draftDiffers(current: VoiceDocument) {
  return (
    draft.value.title !== current.title ||
    draft.value.format !== current.format ||
    draft.value.content !== current.content
  );
}

function confirmDiscard() {
  return window.confirm('Tienes cambios sin guardar. ¿Descartarlos?');
}

function allowLeaving() {
  return !hasUnsavedEdits.value || confirmDiscard();
}

onBeforeRouteLeave(allowLeaving);
onBeforeRouteUpdate(allowLeaving);
// Salir de este documento corta su lectura, no la de otro que llegó mientras tanto.
onBeforeUnmount(() => {
  if (isReadingThis.value) $voice.stop();
});
</script>

<template>
  <WorkspacePage
    id="documento"
    :title="editing ? 'Editar documento' : (document?.title ?? 'Documento')"
    compact-cover
  >
    <template #actions>
      <UTooltip text="Volver a Voz">
        <UButton
          to="/voice"
          icon="i-lucide-arrow-left"
          aria-label="Volver a Voz"
          color="neutral"
          variant="ghost"
          class="text-white hover:bg-white/15"
        />
      </UTooltip>
    </template>

    <template #subtitle>
      <div
        v-if="document && !editing"
        class="mt-1 flex flex-wrap items-center gap-2 text-sm text-muted"
      >
        <span>{{ meta }}</span>
        <UBadge
          v-if="document.origin === 'agent'"
          label="Enviado por un agente"
          icon="i-lucide-bot"
          color="primary"
          variant="subtle"
          size="sm"
        />
      </div>
      <p v-else-if="hasUnsavedEdits" class="mt-1 text-sm text-warning">
        ● Sin guardar
      </p>
    </template>

    <template #title-actions>
      <div v-if="document && !editing" class="flex flex-wrap gap-2">
        <UButton
          label="Eliminar"
          icon="i-lucide-trash-2"
          color="error"
          variant="ghost"
          :loading="deleting"
          @click="deleteDocument"
        />
        <UButton
          label="Editar"
          icon="i-lucide-pencil"
          color="neutral"
          variant="soft"
          @click="startEditing"
        />
        <UButton
          :label="isReadingThis ? 'Desde el inicio' : 'Escuchar'"
          :icon="isReadingThis ? 'i-lucide-rotate-ccw' : 'i-lucide-headphones'"
          :loading="isReadingThis && $voice.state.value.status === 'starting'"
          :disabled="!canListen"
          @click="listen()"
        />
      </div>
      <div v-else-if="editing" class="flex gap-2">
        <UButton
          label="Cancelar"
          color="neutral"
          variant="ghost"
          :disabled="saving"
          @click="cancelEditing"
        />
        <UButton
          label="Guardar"
          icon="i-lucide-save"
          :loading="saving"
          :disabled="!hasUnsavedEdits"
          @click="saveEdits"
        />
      </div>
    </template>

    <div v-if="loading" class="space-y-3" aria-label="Cargando documento">
      <USkeleton class="h-6 w-2/3" />
      <USkeleton class="h-4 w-full" />
      <USkeleton class="h-4 w-5/6" />
      <USkeleton class="h-4 w-4/6" />
    </div>

    <UEmpty
      v-else-if="loadError || !document"
      icon="i-lucide-file-x"
      :title="loadError ?? 'Este documento no existe.'"
      description="Puede que se haya borrado o que el enlace no sea correcto."
      :actions="[
        { label: 'Volver a Voz', icon: 'i-lucide-arrow-left', to: '/voice' },
      ]"
      variant="naked"
    />

    <template v-else-if="editing">
      <UAlert
        v-if="saveError"
        class="mb-5"
        color="error"
        variant="subtle"
        icon="i-lucide-triangle-alert"
        :title="saveError"
        role="alert"
        :actions="
          hasConflict
            ? [{ label: 'Descartar y recargar', onClick: discardAndReload }]
            : []
        "
      />
      <DocumentEditor v-model="draft" :disabled="saving" />
    </template>

    <template v-else>
      <UTabs
        v-model="view"
        :items="VIEW_TABS"
        :content="false"
        variant="link"
        color="neutral"
        class="mb-6 border-b border-default"
      />

      <div v-if="view === 'reading'">
        <div v-if="prepared" class="space-y-4">
          <UAlert
            v-for="notice in prepared.notices"
            :key="notice"
            color="neutral"
            variant="subtle"
            icon="i-lucide-info"
            :title="notice"
          />
          <DocumentBlocks
            :blocks="prepared.blocks"
            :active-block="activeBlock"
            :first-segment-of-block="firstSegmentOfBlock"
            @read-from="listen"
          />
        </div>
        <div v-else class="space-y-3" aria-label="Preparando la lectura">
          <USkeleton v-for="row in 4" :key="row" class="h-4 w-full" />
        </div>
      </div>

      <!-- Original literal: el texto tal como se guardó, sin interpretar. -->
      <pre
        v-else
        class="font-mono text-sm leading-relaxed whitespace-pre-wrap text-toned"
        >{{ document.content }}</pre>
    </template>

    <template #footer>
      <LiveVoiceBar v-if="isReadingThis" />
      <LiveVoiceBar v-else-if="$voice.state.value.documentId" shows-document />
    </template>
  </WorkspacePage>
</template>
