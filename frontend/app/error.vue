<script setup lang="ts">
import type { NuxtError } from '#app';

const props = defineProps<{ error: NuxtError }>();

const title = computed(() =>
  props.error.statusCode === 404
    ? 'Esta página no está aquí'
    : 'Algo interrumpió el camino',
);
</script>

<template>
  <UApp>
    <NuxtLayout>
      <h1 class="focus-title text-[2rem]!">{{ title }}</h1>
      <p class="mt-3 text-base text-muted">
        Puedes volver al inicio y continuar desde allí.
      </p>
      <UButton
        label="Volver al inicio"
        icon="i-lucide-house"
        size="lg"
        block
        class="mt-7"
        @click="clearError({ redirect: '/home' })"
      />
    </NuxtLayout>
  </UApp>
</template>
