<script setup lang="ts">
import type { AutoReadMode } from '../types/voice';

const { mode, setMode } = useAutoReadMode();
const toast = useToast();

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
  set: (value: AutoReadMode) => void changeMode(value),
});

async function changeMode(value: AutoReadMode) {
  try {
    await setMode(value);
  } catch {
    toast.add({
      title: 'No pudimos guardar la opción. Inténtalo de nuevo.',
      color: 'error',
    });
  }
}
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
      Se guarda en tu cuenta: si abres Copilot en otro equipo, también leerá
      allí.
    </p>
  </section>
</template>
