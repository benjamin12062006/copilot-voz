<script setup lang="ts">
import { useClerk } from '@clerk/nuxt/composables';

// Solo se monta con Clerk activo: fuera de él, useClerk no tiene proveedor.
const clerk = useClerk();

function openProfile() {
  clerk.value?.openUserProfile();
}
</script>

<template>
  <UButton
    label="Gestionar cuenta"
    icon="i-lucide-shield-user"
    color="neutral"
    variant="soft"
    @click="openProfile"
  />
</template>
