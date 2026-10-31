<script setup lang="ts">
import { SignIn } from '@clerk/nuxt/components';

const colorMode = useColorMode();

// Variables vigentes de `appearance` de Clerk; colores de los tokens Focus.
const FOCUS_DARK = {
  colorBackground: '#362e38',
  colorForeground: '#fbf7fb',
  colorMutedForeground: '#978d9b',
  colorInput: '#4c4551',
  colorInputForeground: '#fbf7fb',
  colorBorder: '#574f5d',
  colorNeutral: '#fbf7fb',
};

const FOCUS_LIGHT = {
  colorBackground: '#faf8fb',
  colorForeground: '#2b232d',
  colorMutedForeground: '#6e6472',
  colorInput: '#ffffff',
  colorInputForeground: '#2b232d',
  colorBorder: '#cfc6d3',
  colorNeutral: '#2b232d',
};

const appearance = computed(() => ({
  variables: {
    ...(colorMode.value === 'dark' ? FOCUS_DARK : FOCUS_LIGHT),
    colorPrimary: '#8b5cf6',
    colorPrimaryForeground: '#ffffff',
    borderRadius: '0.5rem',
    fontFamily: 'inherit',
  },
  elements: {
    // El formulario vive dentro de nuestra ventana: sin tarjeta propia de Clerk.
    rootBox: { width: '100%' },
    cardBox: { width: '100%', boxShadow: 'none', border: 'none' },
    card: { boxShadow: 'none', padding: '0', background: 'transparent' },
    footer: { background: 'transparent' },
  },
}));
</script>

<template>
  <SignIn
    routing="hash"
    force-redirect-url="/session"
    :appearance="appearance"
  />
</template>
