<script setup lang="ts">
const { state, actions } = useAccess();
const { $accessProvider } = useNuxtApp();

const authenticating = computed(() => state.value.status === 'authenticating');
const showsClerkForm = computed(
  () => authenticating.value && $accessProvider === 'clerk',
);

onBeforeRouteLeave(() => {
  if (authenticating.value) actions.cancelSignIn();
});
</script>

<template>
  <div v-if="state.status === 'signedOut' || authenticating">
    <h1 class="focus-title text-[2.25rem]! sm:text-[2.5rem]!">
      {{ authenticating ? 'Entra a Copilot' : 'Qué bueno verte' }}
    </h1>
    <p class="mt-3 text-base text-muted">
      Escucha tus documentos con una voz clara. Pausa, continúa y vuelve a
      empezar cuando quieras.
    </p>

    <div v-if="showsClerkForm" class="mt-7">
      <ClientOnly><ClerkAccess /></ClientOnly>
      <UButton
        label="Cancelar"
        color="neutral"
        variant="ghost"
        block
        class="mt-4"
        @click="actions.cancelSignIn"
      />
    </div>

    <template v-else>
      <ul class="mt-7 border-t border-default text-sm">
        <li class="flex items-center gap-3 border-b border-default py-2.5">
          <UIcon name="i-lucide-file-text" class="size-4 text-muted" />
          Importa Markdown o texto
        </li>
        <li class="flex items-center gap-3 border-b border-default py-2.5">
          <UIcon name="i-lucide-audio-lines" class="size-4 text-muted" />
          Escucha con controles de reproducción
        </li>
        <li class="flex items-center gap-3 border-b border-default py-2.5">
          <UIcon name="i-lucide-bot" class="size-4 text-muted" />
          Recibe documentos de tus agentes
        </li>
      </ul>

      <UButton
        label="Continuar"
        trailing-icon="i-lucide-arrow-right"
        size="lg"
        block
        class="mt-8"
        :loading="authenticating"
        @click="actions.beginSignIn"
      />
      <p
        v-if="state.status === 'signedOut' && state.notice"
        role="status"
        class="mt-4 text-sm text-muted"
      >
        {{ state.notice }}
      </p>
    </template>
  </div>
  <SessionProgress v-else />
</template>
