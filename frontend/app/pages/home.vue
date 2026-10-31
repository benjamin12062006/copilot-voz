<script setup lang="ts">
definePageMeta({ layout: 'workspace' });

const { state: access } = useAccess();
const library = useDocumentLibrary();

const RECENT_LIMIT = 5;

const firstName = computed(() => {
  if (access.value.status !== 'ready') return '';
  const name = access.value.user.displayName ?? '';
  return name.split(' ')[0] ?? '';
});

const title = computed(() =>
  firstName.value ? `${greetingFor()}, ${firstName.value}` : greetingFor(),
);

const today = new Intl.DateTimeFormat('es', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
}).format(new Date());

const recentDocuments = computed(() =>
  library.documents.value
    .filter((document) => document.origin === 'web')
    .slice(0, RECENT_LIMIT),
);
const agentDocuments = computed(() =>
  library.documents.value
    .filter((document) => document.origin === 'agent')
    .slice(0, RECENT_LIMIT),
);
</script>

<template>
  <WorkspacePage id="inicio" :title="title">
    <template #actions>
      <UButton
        to="/voice/new"
        icon="i-lucide-plus"
        aria-label="Nuevo documento"
        color="neutral"
        variant="ghost"
        class="text-white hover:bg-white/15"
      />
    </template>

    <template #subtitle>
      <p class="mt-1 text-sm text-muted first-letter:uppercase">{{ today }}</p>
    </template>

    <div v-if="library.state.value.status === 'loading'" class="space-y-3">
      <USkeleton v-for="row in 4" :key="row" class="h-10 w-full" />
    </div>

    <UAlert
      v-else-if="library.state.value.status === 'error'"
      color="error"
      variant="subtle"
      icon="i-lucide-cloud-off"
      :title="library.state.value.message"
      :actions="[{ label: 'Reintentar', onClick: () => library.refresh() }]"
    />

    <div v-else class="space-y-10">
      <section aria-labelledby="recientes">
        <h2 id="recientes" class="focus-section-label mb-1">
          Continúa escuchando
        </h2>
        <ul v-if="recentDocuments.length">
          <DocumentRow
            v-for="document in recentDocuments"
            :key="document.id"
            :document="document"
          />
        </ul>
        <UEmpty
          v-else
          icon="i-lucide-file-plus"
          title="Todavía no tienes documentos"
          description="Crea uno o importa un archivo para escucharlo."
          :actions="[{ label: 'Nuevo documento', to: '/voice/new' }]"
          variant="naked"
        />
      </section>

      <section aria-labelledby="agentes">
        <h2 id="agentes" class="focus-section-label mb-1">
          Enviado por agentes
        </h2>
        <ul v-if="agentDocuments.length">
          <DocumentRow
            v-for="document in agentDocuments"
            :key="document.id"
            :document="document"
          />
        </ul>
        <p v-else class="py-3 text-sm text-muted">
          Cuando Codex o Claude Code te envíen un documento, aparecerá aquí.
        </p>
      </section>
    </div>
  </WorkspacePage>
</template>
