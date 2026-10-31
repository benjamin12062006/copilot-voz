<script setup lang="ts">
defineProps<{
  name: 'fingerprint' | 'arrow' | 'user' | 'logout' | 'connection';
}>();
</script>

<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.6"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <template v-if="name === 'fingerprint'">
      <path d="M6.1 3.6a12 12 0 0 1 11.8 0M3.5 7.5a10.8 10.8 0 0 1 17 0" />
      <path
        d="M2.6 12.2a9.4 9.4 0 0 1 18.8 0v1.1a3.2 3.2 0 0 1-6.4 0v-.8a3 3 0 0 0-6 0c0 4.5 2.1 7.9 5.6 9"
      />
      <path
        d="M5.3 18.3a15 15 0 0 1-.7-5.8 7.4 7.4 0 0 1 14.8 0v.7a1.2 1.2 0 0 1-2.4 0v-.7a5 5 0 0 0-10 0 13 13 0 0 0 3.1 8.7"
      />
      <path d="M12 12.3c0 3.7 1.8 6 5 6.3M12 15.3a8.3 8.3 0 0 0 7 5" />
    </template>
    <path v-else-if="name === 'arrow'" d="M5 12h14m-6-6 6 6-6 6" />
    <template v-else-if="name === 'user'">
      <circle cx="12" cy="7.5" r="3.5" />
      <path d="M4 21v-2.5c0-5.3 16-5.3 16 0V21Z" />
    </template>
    <path v-else-if="name === 'logout'" d="M10 4H5v16h5m0-8h11m-4-4 4 4-4 4" />
    <template v-else>
      <path
        d="m3 3 18 18M5 8a12 12 0 0 1 15 1M8 12a7.5 7.5 0 0 1 8 1M11 16a3 3 0 0 1 3 0M2 9l1-1"
      />
      <circle cx="12" cy="20" r=".6" />
    </template>
  </svg>
</template>
