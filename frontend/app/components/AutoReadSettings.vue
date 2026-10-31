<script setup lang="ts">
import type { AutoReadMode } from '../types/voice';

const { mode, setMode } = useAutoReadMode();

const MODE_ITEMS: {
  label: string;
  description: string;
  value: AutoReadMode;
}[] = [
  {
    label: 'Apagado',
    description: 'Los documentos nuevos esperan a que los abras.',
    value: 'off',
  },
  {
    label: 'Documentos de agentes',
    description: 'Lee lo que te envían Codex o Claude Code por el MCP.',
    value: 'agent',
  },
  {
    label: 'Todos los documentos nuevos',
    description: 'También los que creas o importas desde otra pestaña.',
    value: 'all',
  },
];

const selectedMode = computed({
  get: () => mode.value,
  set: (value: AutoReadMode) => setMode(value),
});
</script>

<template>
  <section
    aria-labelledby="auto-read-title"
    class="mt-10 space-y-4 border-t border-default pt-6"
  >
    <div>
      <h2 id="auto-read-title" class="text-lg font-medium">
        Lectura automática
      </h2>
      <p class="mt-1 text-sm text-muted">
        Cuando llega un documento nuevo, Copilot lo lee en voz alta aunque estés
        en otra pestaña. Funciona mientras esta pestaña siga abierta.
      </p>
    </div>
    <URadioGroup v-model="selectedMode" :items="MODE_ITEMS" />
    <p class="text-xs text-dimmed">
      Por ahora se guarda solo en este navegador.
    </p>
  </section>
</template>
