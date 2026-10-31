<script setup lang="ts">
import type { DocumentFormat, DocumentOrigin } from '../../types/documents';

definePageMeta({ layout: 'workspace' });

const route = useRoute();
const library = useDocumentLibrary();

const formatFilter = computed(() =>
  queryValue<DocumentFormat>('format', ['markdown', 'text']),
);
const originFilter = computed(() =>
  queryValue<DocumentOrigin>('origin', ['web', 'agent']),
);

const title = computed(() => {
  if (formatFilter.value) return FORMAT_LABELS[formatFilter.value];
  if (originFilter.value === 'agent') return 'Enviado por agentes';
  return 'Voz';
});

const visibleDocuments = computed(() =>
  library.documents.value.filter(
    (document) =>
      matchesFilter(document.format, formatFilter.value) &&
      matchesFilter(document.origin, originFilter.value),
  ),
);

const isFiltered = computed(() =>
  Boolean(formatFilter.value || originFilter.value),
);

/** Valor de la query solo si es uno de los permitidos; si no, sin filtro. */
function queryValue<T extends string>(
  name: string,
  allowed: readonly T[],
): T | null {
  const value = route.query[name];
  return allowed.find((option) => option === value) ?? null;
}

function matchesFilter<T>(value: T, filter: T | null) {
  return filter === null || value === filter;
}
</script>

<template>
  <WorkspacePage id="voz" :title="title">
    <template #actions>
      <UTooltip text="Importar archivo">
        <UButton
          to="/voice/new"
          icon="i-lucide-file-up"
          aria-label="Importar archivo"
          color="neutral"
          variant="ghost"
          class="text-white hover:bg-white/15"
        />
      </UTooltip>
      <UTooltip text="Nuevo documento">
        <UButton
          to="/voice/new"
          icon="i-lucide-plus"
          aria-label="Nuevo documento"
          color="neutral"
          variant="ghost"
          class="text-white hover:bg-white/15"
        />
      </UTooltip>
    </template>

    <template #subtitle>
      <p
        v-if="library.state.value.status === 'ready'"
        class="mt-1 text-sm text-muted"
      >
        {{ visibleDocuments.length }} documento(s)
        <NuxtLink
          v-if="isFiltered"
          to="/voice"
          class="ms-2 text-primary underline-offset-2 hover:underline"
        >
          Ver todos
        </NuxtLink>
      </p>
    </template>

    <div
      v-if="library.state.value.status === 'loading'"
      class="space-y-3"
      aria-label="Cargando documentos"
    >
      <USkeleton v-for="row in 5" :key="row" class="h-10 w-full" />
    </div>

    <UAlert
      v-else-if="library.state.value.status === 'error'"
      color="error"
      variant="subtle"
      icon="i-lucide-cloud-off"
      :title="library.state.value.message"
      :actions="[{ label: 'Reintentar', onClick: () => library.refresh() }]"
    />

    <ul v-else-if="visibleDocuments.length">
      <DocumentRow
        v-for="document in visibleDocuments"
        :key="document.id"
        :document="document"
      />
    </ul>

    <UEmpty
      v-else
      icon="i-lucide-audio-lines"
      :title="isFiltered ? 'Nada con este filtro' : 'Tu biblioteca está vacía'"
      description="Crea un documento o importa un archivo .md o .txt para escucharlo."
      :actions="[
        { label: 'Nuevo documento', icon: 'i-lucide-plus', to: '/voice/new' },
      ]"
      variant="naked"
    />
  </WorkspacePage>
</template>
