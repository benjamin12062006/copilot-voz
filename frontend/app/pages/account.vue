<script setup lang="ts">
const { state, actions } = useAccess();
const memberSince = computed(() =>
  state.value.status === 'ready'
    ? new Intl.DateTimeFormat('es', {
        day: 'numeric',
        month: 'numeric',
        year: 'numeric',
        timeZone: 'America/New_York',
      }).format(new Date(state.value.user.createdAt))
    : '',
);
</script>

<template>
  <div v-if="state.status === 'ready'">
    <p class="eyebrow">Dentro de tu cuenta</p>
    <div
      class="mt-6 flex size-16 items-center justify-center rounded-full bg-sage"
    >
      <AppIcon name="user" class="size-7" />
    </div>
    <h1
      class="mt-7 text-[29px] leading-tight tracking-[-0.02em] sm:text-[32px]"
    >
      {{ state.user.displayName ?? 'Bienvenido a tu espacio.' }}
    </h1>
    <p class="mt-4 text-base leading-relaxed">
      Tu sesión está activa y tu cuenta está lista.
    </p>
    <dl class="mt-6 border-t border-muted/30 pt-6">
      <dt class="eyebrow">Correo de tu cuenta</dt>
      <dd class="mt-2 text-base break-words select-text">
        {{ state.user.email ?? 'Sin correo disponible' }}
      </dd>
      <dt class="eyebrow mt-7">Miembro desde</dt>
      <dd class="mt-2 text-base">
        <time :datetime="state.user.createdAt">{{ memberSince }}</time>
      </dd>
    </dl>
    <button
      type="button"
      class="action-secondary mt-10"
      @click="actions.signOut"
    >
      <AppIcon name="logout" class="size-5" />
      Cerrar sesión
    </button>
  </div>
  <SessionProgress v-else />
</template>
