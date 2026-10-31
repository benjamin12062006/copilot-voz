<script setup lang="ts">
import type { AgentToken } from '../services/account';
import { buildMcpAndSkillPrompt } from '../utils/mcp-skill-prompt';

const { $account, $accessProvider } = useNuxtApp();
const config = useRuntimeConfig().public;
const library = useDocumentLibrary();
const tokens = ref<AgentToken[]>([]);
const issuedToken = ref('');
const tokenName = ref('Mi agente');
const retentionLimit = ref(20);
const savedLimit = ref(20);
const loading = ref(true);
const busy = ref(false);
const error = ref('');
const copied = ref(false);
const copiedSkill = ref(false);
const connected = computed(
  () => config.dataSource === 'api' && $accessProvider === 'clerk',
);
const toast = useToast();

onMounted(load);
onBeforeUnmount(() => {
  issuedToken.value = '';
});

async function load() {
  if (!connected.value) {
    loading.value = false;
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const [items, preference] = await Promise.all([
      $account.tokens(),
      $account.preferences(),
    ]);
    tokens.value = items;
    retentionLimit.value = savedLimit.value = preference.retentionLimit;
  } catch (failure) {
    error.value =
      failure instanceof Error
        ? failure.message
        : 'No pudimos cargar tu configuración.';
  } finally {
    loading.value = false;
  }
}

async function generateToken() {
  issuedToken.value = '';
  copied.value = false;
  copiedSkill.value = false;
  busy.value = true;
  error.value = '';
  try {
    const issued = await $account.issue(tokenName.value.trim() || 'Mi agente');
    // Solo memoria de este componente: no persistir la credencial.
    issuedToken.value = issued.token;
    tokens.value = await $account.tokens();
  } catch (failure) {
    showFailure(failure);
  } finally {
    busy.value = false;
  }
}

async function copyToken() {
  try {
    await navigator.clipboard.writeText(issuedToken.value);
    copied.value = true;
  } catch {
    error.value =
      'No pudimos copiar. Selecciona el token y cópialo manualmente.';
  }
}

async function copyMcpSkillContext() {
  try {
    const prompt = buildMcpAndSkillPrompt(config.apiBaseUrl, issuedToken.value);
    await navigator.clipboard.writeText(prompt);
    copiedSkill.value = true;
    toast.add({
      title: issuedToken.value
        ? 'Skill /voz-redaccion y conexión MCP (con tu token) copiadas'
        : 'Skill /voz-redaccion e instrucciones MCP copiadas',
      color: 'success',
      icon: 'i-lucide-check',
    });
  } catch {
    error.value = 'No pudimos copiar el contexto para el agente.';
  }
}

async function revokeToken(token: AgentToken) {
  if (
    !window.confirm(
      `¿Revocar «${token.name}»? Ese agente ya no podrá enviar documentos.`,
    )
  )
    return;
  busy.value = true;
  error.value = '';
  try {
    await $account.revoke(token.id);
    issuedToken.value = '';
    tokens.value = await $account.tokens();
  } catch (failure) {
    showFailure(failure);
  } finally {
    busy.value = false;
  }
}

async function saveRetention() {
  if (
    !Number.isInteger(retentionLimit.value) ||
    retentionLimit.value < 1 ||
    retentionLimit.value > 100
  ) {
    error.value = 'Elige un número entero entre 1 y 100.';
    return;
  }
  const removesExisting = library.documents.value.length > retentionLimit.value;
  if (
    removesExisting &&
    !window.confirm(
      `Se conservarán los ${retentionLimit.value} documentos más recientes y se eliminarán los demás. ¿Continuar?`,
    )
  )
    return;
  busy.value = true;
  error.value = '';
  try {
    const saved = await $account.setRetention(retentionLimit.value);
    savedLimit.value = saved.retentionLimit;
    await library.refresh();
    toast.add({
      title: 'Límite guardado',
      color: 'success',
      icon: 'i-lucide-check',
    });
  } catch (failure) {
    showFailure(failure);
  } finally {
    busy.value = false;
  }
}

function showFailure(failure: unknown) {
  error.value =
    failure instanceof Error
      ? failure.message
      : 'No pudimos completar la operación.';
}
function isActive(token: AgentToken) {
  return !token.revokedAt && Date.parse(token.expiresAt) > Date.now();
}
function expiry(token: AgentToken) {
  return new Date(token.expiresAt).toLocaleDateString('es');
}
</script>

<template>
  <div class="mt-10 space-y-8">
    <UAlert
      v-if="!connected"
      title="Estas opciones requieren tu sesión y la conexión con la API."
      color="neutral"
      variant="subtle"
    />
    <UAlert
      v-if="error"
      :title="error"
      color="error"
      variant="subtle"
      role="alert"
      :actions="[{ label: 'Recargar', onClick: load }]"
    />
    <section
      aria-labelledby="mcp-title"
      class="space-y-4 border-t border-default pt-6"
    >
      <div class="flex items-start justify-between gap-4">
        <div>
          <h2 id="mcp-title" class="text-lg font-medium">
            Acceso para agentes MCP
          </h2>
          <p class="mt-1 text-sm text-muted">
            Genera un token personal para que tu agente envíe Markdown a tu
            biblioteca. Caduca en 30 días y puedes revocarlo aquí.
          </p>
        </div>
        <UTooltip
          text="Copiar contexto de conexión MCP y skill /voz-redaccion para pegar en tu chat de IA"
        >
          <UButton
            :label="
              copiedSkill ? 'Skill copiada' : 'Copiar skill /voz-redaccion'
            "
            :icon="copiedSkill ? 'i-lucide-check' : 'i-lucide-copy'"
            color="neutral"
            variant="soft"
            size="sm"
            class="shrink-0"
            @click="copyMcpSkillContext"
          />
        </UTooltip>
      </div>
      <div class="flex flex-wrap items-end gap-3">
        <UFormField label="Nombre del agente"
          ><UInput
            v-model="tokenName"
            maxlength="80"
            placeholder="Mi agente"
            :disabled="!connected || busy"
        /></UFormField>
        <UButton
          label="Generar token"
          icon="i-lucide-key-round"
          :loading="busy"
          :disabled="!connected || loading"
          @click="generateToken"
        />
      </div>
      <div v-if="issuedToken" class="space-y-3 rounded-lg bg-elevated p-4">
        <p class="text-sm">Cópialo ahora: no volverá a mostrarse.</p>
        <textarea
          :value="issuedToken"
          readonly
          aria-label="Token MCP generado"
          class="w-full rounded-md border border-default bg-default p-3 font-mono text-sm break-all"
          rows="3"
          spellcheck="false"
        />
        <div class="flex flex-wrap gap-2">
          <UButton
            :label="copied ? 'Copiado' : 'Copiar token'"
            icon="i-lucide-copy"
            @click="copyToken"
          />
          <UButton
            :label="
              copiedSkill
                ? 'Skill + token copiados'
                : 'Copiar skill /voz-redaccion con este token'
            "
            :icon="copiedSkill ? 'i-lucide-check' : 'i-lucide-copy'"
            color="neutral"
            variant="soft"
            @click="copyMcpSkillContext"
          />
          <UButton
            label="Ocultar"
            color="neutral"
            variant="ghost"
            @click="issuedToken = ''"
          />
        </div>
      </div>
      <USkeleton v-if="loading" class="h-12 w-full" />
      <ul v-else class="divide-y divide-default">
        <li
          v-for="token in tokens"
          :key="token.id"
          class="flex items-center justify-between gap-4 py-3"
        >
          <div>
            <p class="text-sm">{{ token.name }}</p>
            <p class="text-xs text-muted">
              {{ token.revokedAt ? 'Revocado' : `Caduca ${expiry(token)}` }}
            </p>
          </div>
          <UButton
            v-if="isActive(token)"
            label="Revocar"
            color="error"
            variant="ghost"
            :disabled="busy"
            @click="revokeToken(token)"
          />
        </li>
      </ul>
    </section>
    <section
      aria-labelledby="storage-title"
      class="space-y-4 border-t border-default pt-6"
    >
      <div>
        <h2 id="storage-title" class="text-lg font-medium">Almacenamiento</h2>
        <p class="mt-1 text-sm text-muted">
          Al superar el límite, se eliminan automáticamente los documentos más
          antiguos. Este límite se aplica también a los textos enviados por
          agentes.
        </p>
      </div>
      <div class="flex flex-wrap items-end gap-3">
        <UFormField
          label="Documentos que quieres conservar"
          help="Entre 1 y 100. Si reduces el límite, se retiran los más antiguos."
        >
          <UInput
            v-model.number="retentionLimit"
            type="number"
            min="1"
            max="100"
            step="1"
            :disabled="!connected || busy || loading"
          />
        </UFormField>
        <UButton
          label="Guardar límite"
          :loading="busy"
          :disabled="!connected || loading || retentionLimit === savedLimit"
          @click="saveRetention"
        />
      </div>
    </section>
  </div>
</template>
