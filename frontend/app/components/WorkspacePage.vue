<script setup lang="ts">
/**
 * Estructura común de cada vista del espacio de trabajo, como en Focus:
 * cabecera ilustrada, título grande y fino y contenido en filas.
 */
withDefaults(
  defineProps<{ id: string; title: string; compactCover?: boolean }>(),
  { compactCover: false },
);
</script>

<template>
  <UDashboardPanel :id="id" :ui="{ body: 'p-0 sm:p-0 gap-0 sm:gap-0' }">
    <template #body>
      <FocusCover :compact="compactCover">
        <template #leading>
          <UDashboardSidebarToggle
            color="neutral"
            variant="soft"
            class="bg-black/25 text-white hover:bg-black/35"
          />
        </template>
        <template #actions>
          <slot name="actions" />
        </template>
      </FocusCover>

      <div
        class="mx-auto w-full max-w-4xl flex-1 px-5 pt-8 pb-12 sm:px-12 sm:pt-10"
      >
        <header class="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div class="min-w-0">
            <h1 class="focus-title break-words">{{ title }}</h1>
            <slot name="subtitle" />
          </div>
          <slot name="title-actions" />
        </header>

        <slot />
      </div>

      <!-- Por defecto, la lectura en curso (p. ej. automática) se controla desde cualquier vista. -->
      <slot name="footer">
        <LiveVoiceBar v-if="$voice.state.value.documentId" shows-document />
      </slot>
    </template>
  </UDashboardPanel>
</template>
