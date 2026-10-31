<script setup lang="ts">
import { DocumentFailure, type DocumentDraft } from '../../types/documents';

definePageMeta({ layout: 'workspace' });

const { $documents } = useNuxtApp();
const library = useDocumentLibrary();
const toast = useToast();

const EMPTY_DRAFT: DocumentDraft = {
  title: '',
  format: 'markdown',
  content: '',
};

const draft = ref<DocumentDraft>({ ...EMPTY_DRAFT });
const saving = ref(false);
const saveError = ref<string | null>(null);

const hasChanges = computed(() =>
  Boolean(draft.value.title.trim() || draft.value.content.trim()),
);

async function save() {
  saving.value = true;
  saveError.value = null;
  const created = await createDocument();
  saving.value = false;
  if (!created) return;

  draft.value = { ...EMPTY_DRAFT };
  toast.add({
    title: 'Documento guardado',
    icon: 'i-lucide-check',
    color: 'success',
  });
  void library.refresh();
  await navigateTo(`/voice/${created.id}`);
}

/** Si falla, el borrador sigue en pantalla: nunca se pierde lo escrito. */
async function createDocument() {
  try {
    return await $documents.create(draft.value);
  } catch (error) {
    saveError.value =
      error instanceof DocumentFailure
        ? error.message
        : 'No pudimos guardar. Tu borrador sigue aquí.';
    return null;
  }
}

onBeforeRouteLeave(() => {
  if (!hasChanges.value || saving.value) return true;
  return window.confirm(
    'Tienes un documento sin guardar. ¿Salir y descartarlo?',
  );
});
</script>

<template>
  <WorkspacePage id="nuevo" title="Nuevo documento" compact-cover>
    <template #subtitle>
      <p class="mt-1 text-sm text-muted">
        <span v-if="hasChanges" class="text-warning">● Sin guardar</span>
        <span v-else
          >Escribe, pega o importa el texto que quieres escuchar.</span
        >
      </p>
    </template>

    <template #title-actions>
      <div class="flex gap-2">
        <UButton label="Cancelar" color="neutral" variant="ghost" to="/voice" />
        <UButton
          label="Guardar"
          icon="i-lucide-save"
          :loading="saving"
          :disabled="!hasChanges"
          @click="save"
        />
      </div>
    </template>

    <UAlert
      v-if="saveError"
      class="mb-5"
      color="error"
      variant="subtle"
      icon="i-lucide-triangle-alert"
      :title="saveError"
      role="alert"
    />

    <DocumentEditor v-model="draft" :disabled="saving" />
  </WorkspacePage>
</template>
