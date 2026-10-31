<script setup lang="ts">
import { SignIn } from '@clerk/nuxt/components';
</script>

<template>
  <SignIn routing="hash" force-redirect-url="/session" />
</template>
