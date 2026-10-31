<script setup lang="ts">
import {
  MAX_DOCUMENT_BYTES,
  type DocumentDraft,
  type DocumentFormat,
} from '../types/documents';

const draft = defineModel<DocumentDraft>({ required: true });
defineProps<{ disabled?: boolean }>();

const FORMAT_ITEMS = [
  { label: 'Markdown', value: 'markdown', icon: 'i-lucide-file-code-2' },
  { label: 'Texto', value: 'text', icon: 'i-lucide-file-text' },
] satisfies { label: string; value: DocumentFormat; icon: string }[];

const importedFile = ref<File | null>(null);
const importError = ref<string | null>(null);

function update(changes: Partial<DocumentDraft>) {
  draft.value = { ...draft.value, ...changes };
}

watch(importedFile, async (file) => {
  if (!file) return;
  importError.value = null;
  await importFile(file);
  // Vacía el selector para poder importar otra vez el mismo archivo.
  importedFile.value = null;
});

async function importFile(file: File) {
  if (file.size > MAX_DOCUMENT_BYTES) {
    importError.value = 'El archivo supera el límite de 1 MB.';
    return;
  }
  const content = await readUtf8(file);
  if (content === null) {
    importError.value = 'El archivo no es texto UTF-8 válido.';
    return;
  }
  update({
    title: draft.value.title.trim() || titleFromFileName(file.name),
    format: formatFromFileName(file.name),
    content,
  });
}

/** null si el archivo no es UTF-8: `fatal` evita sustituir bytes en silencio. */
async function readUtf8(file: File): Promise<string | null> {
  try {
    return new TextDecoder('utf-8', { fatal: true }).decode(
      await file.arrayBuffer(),
    );
  } catch {
    return null;
  }
}

function titleFromFileName(name: string) {
  return name.replace(/\.(md|markdown|txt)$/i, '');
}

function formatFromFileName(name: string): DocumentFormat {
  return /\.(md|markdown)$/i.test(name) ? 'markdown' : 'text';
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <UFormField label="Título" name="title" required>
      <UInput
        :model-value="draft.title"
        placeholder="Por ejemplo: Notas de la reunión"
        size="xl"
        class="w-full"
        :disabled="disabled"
        @update:model-value="update({ title: String($event) })"
      />
    </UFormField>

    <div class="flex flex-wrap items-end gap-4">
      <UFormField label="Formato" name="format">
        <USelect
          :model-value="draft.format"
          :items="FORMAT_ITEMS"
          class="w-44"
          :disabled="disabled"
          @update:model-value="update({ format: $event })"
        />
      </UFormField>

      <UFileUpload
        v-model="importedFile"
        accept=".md,.markdown,.txt,text/markdown,text/plain"
        label="Importar .md o .txt"
        description="Hasta 1 MB, UTF-8"
        icon="i-lucide-file-up"
        layout="list"
        :preview="false"
        :disabled="disabled"
        class="min-w-64 flex-1"
      />
    </div>

    <UAlert
      v-if="importError"
      color="error"
      variant="subtle"
      icon="i-lucide-file-warning"
      :title="importError"
    />

    <UFormField
      label="Contenido"
      name="content"
      required
      :hint="draft.format === 'markdown' ? 'Markdown' : 'Texto plano'"
    >
      <UTextarea
        :model-value="draft.content"
        :rows="14"
        autoresize
        :maxrows="30"
        placeholder="Escribe o pega el texto que quieres escuchar…"
        class="w-full"
        :ui="{ base: draft.format === 'markdown' ? 'font-mono text-sm' : '' }"
        :disabled="disabled"
        @update:model-value="update({ content: String($event) })"
      />
    </UFormField>
  </div>
</template>
