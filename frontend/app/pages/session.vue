<script setup lang="ts">
const { state, actions } = useAccess();

const progress = computed(() => {
  if (state.value.status === 'signingOut') return 'Cerrando tu sesión…';
  if (state.value.status === 'preparingProfile') return 'Preparando tu cuenta…';
  return 'Recuperando tu sesión…';
});
</script>

<template>
  <div v-if="state.status === 'error'">
    <h1 class="focus-title text-[2rem]!">Vamos a intentarlo de nuevo</h1>
    <UAlert
      class="mt-5"
      color="error"
      variant="subtle"
      icon="i-lucide-wifi-off"
      :title="state.message"
      role="alert"
    />
    <UButton
      label="Reintentar"
      icon="i-lucide-rotate-cw"
      size="lg"
      block
      class="mt-6"
      @click="actions.retry"
    />
    <UButton
      v-if="state.stage !== 'configuration'"
      label="Volver al inicio"
      color="neutral"
      variant="ghost"
      block
      class="mt-2"
      @click="actions.signOut"
    />
  </div>

  <div v-else>
    <SessionProgress :message="progress" />
    <UButton
      v-if="state.status === 'preparingProfile'"
      label="Cancelar"
      color="neutral"
      variant="ghost"
      block
      @click="actions.signOut"
    />
  </div>
</template>
