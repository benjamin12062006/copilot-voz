<script setup lang="ts">
withDefaults(defineProps<{ message?: string }>(), {
  message: 'Recuperando tu sesión…',
});
</script>

<template>
  <div role="status" aria-live="polite" class="py-10 text-center">
    <span
      aria-hidden="true"
      class="mx-auto mb-6 block size-9 animate-spin rounded-full border-2 border-sage border-t-ink motion-reduce:animate-none"
    />
    <p class="text-lg">{{ message }}</p>
  </div>
</template>
