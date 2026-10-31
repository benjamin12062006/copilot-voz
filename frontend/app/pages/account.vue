<script setup lang="ts">
definePageMeta({ layout: 'workspace' });

const { state, actions } = useAccess();
const { $accessProvider } = useNuxtApp();
const config = useRuntimeConfig().public;

const PROVIDER_LABELS = {
  clerk: 'Clerk',
  preview: 'Vista previa local (sin Clerk)',
  none: 'Sin configurar',
};

const user = computed(() =>
  state.value.status === 'ready' ? state.value.user : null,
);

const memberSince = computed(() => {
  if (!user.value) return '';
  return new Intl.DateTimeFormat('es', { dateStyle: 'long' }).format(
    new Date(user.value.createdAt),
  );
});

const dataSourceLabel = computed(() =>
  config.dataSource === 'api'
    ? 'Biblioteca conectada · voz del sistema'
    : 'Datos simulados en este navegador',
);
</script>

<template>
  <WorkspacePage
    id="cuenta"
    :title="user?.displayName ?? 'Tu cuenta'"
    compact-cover
  >
    <template #title-actions>
      <div class="flex gap-2">
        <ClerkProfileButton v-if="$accessProvider === 'clerk'" />
        <UButton
          label="Cerrar sesión"
          icon="i-lucide-log-out"
          color="neutral"
          variant="ghost"
          @click="actions.signOut"
        />
      </div>
    </template>

    <dl v-if="user">
      <div class="flex justify-between gap-4 border-b border-default py-3">
        <dt class="text-sm text-muted">Correo</dt>
        <dd class="text-sm break-all text-default">
          {{ user.email ?? 'Sin correo disponible' }}
        </dd>
      </div>
      <div class="flex justify-between gap-4 border-b border-default py-3">
        <dt class="text-sm text-muted">Miembro desde</dt>
        <dd class="text-sm text-default">
          <time :datetime="user.createdAt">{{ memberSince }}</time>
        </dd>
      </div>
      <div class="flex justify-between gap-4 border-b border-default py-3">
        <dt class="text-sm text-muted">Acceso</dt>
        <dd class="text-sm text-default">
          {{ PROVIDER_LABELS[$accessProvider] }}
        </dd>
      </div>
      <div class="flex justify-between gap-4 border-b border-default py-3">
        <dt class="text-sm text-muted">Documentos y voz</dt>
        <dd class="text-sm text-default">{{ dataSourceLabel }}</dd>
      </div>
    </dl>
    <AccountStorage v-if="user" />
  </WorkspacePage>
</template>
