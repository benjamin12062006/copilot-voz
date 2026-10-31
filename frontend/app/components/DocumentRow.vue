<script setup lang="ts">
import type { DocumentSummary } from '../types/documents';

const props = defineProps<{ document: DocumentSummary }>();

const meta = computed(() =>
  [
    FORMAT_LABELS[props.document.format],
    `${props.document.wordCount} palabras`,
    formatRelativeDate(props.document.updatedAt),
  ].join(' · '),
);
</script>

<template>
  <li class="border-b border-default">
    <NuxtLink
      :to="`/voice/${document.id}`"
      class="group -mx-2 flex items-start gap-3 rounded-md px-2 py-2.5 transition-colors hover:bg-elevated/50 focus-visible:bg-elevated/50 focus-visible:outline-2 focus-visible:outline-primary"
    >
      <!-- Círculo de la fila, como el de las tareas de Focus. -->
      <span
        aria-hidden="true"
        class="mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full ring-1 ring-(--ui-text-dimmed) group-hover:ring-(--ui-text-muted)"
      >
        <span
          class="size-1.5 rounded-full"
          :class="FORMAT_DOT_CLASSES[document.format]"
        />
      </span>

      <span class="min-w-0 flex-1">
        <span class="block truncate text-sm text-default">
          {{ document.title }}
        </span>
        <span class="mt-0.5 block text-xs text-muted">{{ meta }}</span>
      </span>

      <UBadge
        v-if="document.origin === 'agent'"
        label="Agente"
        icon="i-lucide-bot"
        color="primary"
        variant="subtle"
        size="sm"
        class="shrink-0"
      />
    </NuxtLink>
  </li>
</template>
