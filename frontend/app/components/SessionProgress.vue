<script setup lang="ts">
withDefaults(defineProps<{ message?: string }>(), {
  message: 'Recuperando tu sesión…',
});
</script>

<template>
  <div role="status" aria-live="polite" class="py-10 text-center">
    <UIcon
      name="i-lucide-loader-circle"
      class="mx-auto mb-5 size-8 animate-spin text-muted motion-reduce:animate-none"
    />
    <p class="text-base text-toned">{{ message }}</p>
  </div>
</template>
