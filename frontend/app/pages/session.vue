<script setup lang="ts">
const { state, actions } = useAccess();
const progress = computed(() => {
  if (state.value.status === 'signingOut') return 'Cerrando tu sesión…';
  if (state.value.status === 'preparingProfile') return 'Preparando tu cuenta…';
  return 'Recuperando tu sesión…';
});
</script>

<template>
  <div>
    <p class="eyebrow">Tu cuenta</p>
    <template v-if="state.status === 'error'">
      <AppIcon name="connection" class="mt-7 size-10" />
      <h1 class="mt-5 text-[28px] leading-tight">
        Vamos a intentarlo de nuevo.
      </h1>
      <p role="alert" class="mt-4 text-base leading-relaxed">
        {{ state.message }}
      </p>
      <button type="button" class="action-primary mt-7" @click="actions.retry">
        Reintentar
      </button>
      <div v-if="state.stage !== 'configuration'" class="mt-3 text-center">
        <button type="button" class="action-text" @click="actions.signOut">
          Volver al inicio
        </button>
      </div>
    </template>
    <template v-else>
      <SessionProgress :message="progress" />
      <div v-if="state.status === 'preparingProfile'" class="text-center">
        <button type="button" class="action-text" @click="actions.signOut">
          Cancelar
        </button>
      </div>
    </template>
  </div>
</template>
