<script setup lang="ts">
const { state, actions } = useAccess();
const active = computed(() => state.value.status === 'authenticating');
onBeforeRouteLeave(() => {
  if (active.value) actions.cancelSignIn();
});
</script>

<template>
  <div v-if="state.status === 'signedOut' || state.status === 'authenticating'">
    <p class="eyebrow">Tu espacio personal</p>
    <h1
      class="mt-4 text-[29px] leading-tight tracking-[-0.015em] sm:text-[32px]"
    >
      {{ active ? 'Entra a Copilot.' : 'Qué bueno verte.' }}
    </h1>
    <p class="mt-4 text-lg leading-relaxed">
      Entra o crea tu cuenta para comenzar.
    </p>
    <template v-if="active">
      <ClientOnly><ClerkAccess /></ClientOnly>
      <div class="mt-6 flex justify-center">
        <button type="button" class="action-text" @click="actions.cancelSignIn">
          Cancelar
        </button>
      </div>
    </template>
    <template v-else>
      <AppIcon name="fingerprint" class="mx-auto mt-10 mb-9 size-16" />
      <button type="button" class="action-primary" @click="actions.beginSignIn">
        <AppIcon name="arrow" class="size-5" />Continuar
      </button>
      <p
        v-if="state.status === 'signedOut' && state.notice"
        role="status"
        class="mt-4 text-sm leading-relaxed text-muted"
      >
        {{ state.notice }}
      </p>
    </template>
    <footer
      class="mt-10 border-t border-muted/30 pt-6 text-center text-sm text-muted"
    >
      Tu cuenta, bajo tu control.
    </footer>
  </div>
  <SessionProgress v-else />
</template>
