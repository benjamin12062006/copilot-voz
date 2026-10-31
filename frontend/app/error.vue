<script setup lang="ts">
import type { NuxtError } from '#app';
defineProps<{ error: NuxtError }>();
</script>

<template>
  <NuxtLayout>
    <p class="eyebrow">Copilot</p>
    <h1 class="mt-5 text-3xl">
      {{
        error.statusCode === 404
          ? 'Esta página no está aquí.'
          : 'Algo interrumpió el camino.'
      }}
    </h1>
    <p class="mt-4 leading-relaxed">
      Puedes volver a tu cuenta y continuar desde allí.
    </p>
    <button
      type="button"
      class="action-primary mt-8"
      @click="clearError({ redirect: '/auth' })"
    >
      Volver al inicio
    </button>
  </NuxtLayout>
</template>
