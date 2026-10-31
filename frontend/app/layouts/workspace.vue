<script setup lang="ts">
import type { DropdownMenuItem, NavigationMenuItem } from '@nuxt/ui';
import type { DocumentFormat } from '../types/documents';

const { state: access, actions } = useAccess();
const library = useDocumentLibrary();
const colorMode = useColorMode();

const user = computed(() =>
  access.value.status === 'ready' ? access.value.user : null,
);
const userName = computed(
  () => user.value?.displayName ?? user.value?.email ?? 'Tu cuenta',
);

const agentCount = computed(
  () => library.documents.value.filter((doc) => doc.origin === 'agent').length,
);

function countByFormat(format: DocumentFormat) {
  return library.documents.value.filter((doc) => doc.format === format).length;
}

const workspaceItems = computed<NavigationMenuItem[]>(() => [
  { label: 'Inicio', icon: 'i-lucide-house', to: '/home' },
  {
    label: 'Voz',
    icon: 'i-lucide-audio-lines',
    to: '/voice',
    exact: true,
    badge: String(library.documents.value.length),
  },
  { label: 'Nuevo documento', icon: 'i-lucide-plus', to: '/voice/new' },
]);

const formatItems = computed(() =>
  (['markdown', 'text'] as const).map((format) => ({
    label: FORMAT_LABELS[format],
    to: { path: '/voice', query: { format } },
    dot: FORMAT_DOT_CLASSES[format],
    count: countByFormat(format),
  })),
);

const accountItems = computed<DropdownMenuItem[][]>(() => [
  [{ label: 'Perfil', icon: 'i-lucide-user', to: '/account' }],
  [
    {
      label: colorMode.value === 'dark' ? 'Modo claro' : 'Modo oscuro',
      icon: colorMode.value === 'dark' ? 'i-lucide-sun' : 'i-lucide-moon',
      onSelect: toggleColorMode,
    },
  ],
  [
    {
      label: 'Cerrar sesión',
      icon: 'i-lucide-log-out',
      color: 'error',
      onSelect: () => void actions.signOut(),
    },
  ],
]);

function toggleColorMode() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark';
}

// Los documentos enviados por agentes aparecen al volver a la ventana.
function refreshOnFocus() {
  void library.refresh();
}

onMounted(() => {
  void library.refresh();
  window.addEventListener('focus', refreshOnFocus);
});
onBeforeUnmount(() => window.removeEventListener('focus', refreshOnFocus));
</script>

<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar
      id="lateral"
      collapsible
      :default-size="17"
      :min-size="15"
      :max-size="22"
      resizable
      :ui="{
        root: 'bg-muted border-e-0',
        content: 'bg-muted',
        header: 'h-14',
        footer: 'border-t border-black/10 py-3',
      }"
    >
      <template #header="{ collapsed }">
        <NuxtLink
          to="/home"
          class="flex items-center gap-2 text-sm font-medium text-toned"
        >
          <UIcon name="i-lucide-audio-waveform" class="size-5 text-primary" />
          <span v-if="!collapsed">Copilot</span>
        </NuxtLink>
      </template>

      <template #default="{ collapsed }">
        <!-- Tarjetas resumen, como «All» e «Inbox» en la referencia. -->
        <div v-if="!collapsed" class="grid grid-cols-2 gap-2">
          <NuxtLink
            to="/voice"
            class="rounded-lg bg-accented/70 p-2.5 ring-1 ring-white/5 transition-colors hover:bg-accented"
          >
            <div class="flex items-start justify-between text-muted">
              <UIcon name="i-lucide-library" class="size-4" />
              <span class="text-sm tabular-nums">{{
                library.documents.value.length
              }}</span>
            </div>
            <p class="mt-2 text-sm text-default">Todos</p>
          </NuxtLink>
          <NuxtLink
            :to="{ path: '/voice', query: { origin: 'agent' } }"
            class="rounded-lg bg-accented/70 p-2.5 ring-1 ring-white/5 transition-colors hover:bg-accented"
          >
            <div class="flex items-start justify-between text-muted">
              <UIcon name="i-lucide-bot" class="size-4" />
              <span class="text-sm tabular-nums">{{ agentCount }}</span>
            </div>
            <p class="mt-2 text-sm text-default">Agentes</p>
          </NuxtLink>
        </div>

        <div>
          <p v-if="!collapsed" class="focus-section-label mb-1 px-2.5">
            Espacio
          </p>
          <UNavigationMenu
            :items="workspaceItems"
            orientation="vertical"
            :collapsed="collapsed"
            tooltip
            :ui="{
              link: 'py-1.5 data-active:before:bg-elevated',
              linkTrailingBadge: 'bg-transparent text-dimmed font-normal',
            }"
          />
        </div>

        <div v-if="!collapsed">
          <p class="focus-section-label mb-1 px-2.5">Formatos</p>
          <ul>
            <li v-for="item in formatItems" :key="item.label">
              <NuxtLink
                :to="item.to"
                class="flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-sm text-default transition-colors hover:bg-elevated/60"
              >
                <span class="size-2.5 rounded-full" :class="item.dot" />
                <span class="flex-1">{{ item.label }}</span>
                <span class="text-xs text-dimmed tabular-nums">{{
                  item.count
                }}</span>
              </NuxtLink>
            </li>
          </ul>
        </div>
      </template>

      <template #footer="{ collapsed }">
        <UDropdownMenu
          :items="accountItems"
          :content="{ align: 'start', side: 'top' }"
          class="w-full"
        >
          <UButton
            color="neutral"
            variant="ghost"
            block
            :square="collapsed"
            class="justify-start gap-2.5"
            :aria-label="`Menú de ${userName}`"
          >
            <UAvatar :alt="userName" size="sm" />
            <span v-if="!collapsed" class="min-w-0 flex-1 text-left">
              <span class="block truncate text-sm text-default">{{
                userName
              }}</span>
              <span
                v-if="user?.email"
                class="block truncate text-xs text-muted"
                >{{ user.email }}</span
              >
            </span>
            <UIcon
              v-if="!collapsed"
              name="i-lucide-chevrons-up-down"
              class="size-4 text-dimmed"
            />
          </UButton>
        </UDropdownMenu>
      </template>
    </UDashboardSidebar>

    <slot v-if="access.status === 'ready'" />
    <div v-else class="flex flex-1 items-center justify-center">
      <SessionProgress />
    </div>
  </UDashboardGroup>
</template>
