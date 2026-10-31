<script setup lang="ts">
import { SPEECH_RATES } from '../services/live-voice';
import type { LiveVoiceStatus } from '../types/voice';

const { $voice } = useNuxtApp();
const voice = $voice.state;

const STATUS_LABELS: Record<LiveVoiceStatus, string> = {
  idle: 'Sin lectura',
  starting: 'Preparando la voz…',
  speaking: 'Leyendo en vivo',
  paused: 'En pausa',
  ended: 'Lectura terminada',
  error: 'La lectura se detuvo',
  unsupported: 'Voz no disponible',
};

const RATE_ITEMS = SPEECH_RATES.map((rate) => ({
  label: `${rate.toLocaleString('es')}×`,
  value: rate,
}));

const isSpeaking = computed(() => voice.value.status === 'speaking');
const canControl = computed(() =>
  ['speaking', 'paused', 'ended', 'error'].includes(voice.value.status),
);
const statusText = computed(
  () => voice.value.message ?? STATUS_LABELS[voice.value.status],
);
const progressText = computed(
  () => `Frase ${voice.value.segmentIndex + 1} de ${voice.value.segmentCount}`,
);

/** La frase actual partida en tres para resaltar la palabra que suena. */
const caption = computed(() => {
  const { segmentText, wordStart, wordLength } = voice.value;
  if (wordStart === null || wordLength === 0) {
    return { before: segmentText, word: '', after: '' };
  }
  return {
    before: segmentText.slice(0, wordStart),
    word: segmentText.slice(wordStart, wordStart + wordLength),
    after: segmentText.slice(wordStart + wordLength),
  };
});

const voiceItems = computed(() =>
  $voice.voices.value.map((option) => ({
    label: option.label,
    value: option.name,
  })),
);
const selectedVoice = computed(
  () => $voice.preferences.value.voiceName ?? voiceItems.value[0]?.value,
);

function onJump(value: number | number[] | undefined) {
  if (typeof value === 'number') $voice.jumpTo(value);
}

// Espacio: pausa o continúa. Flechas: frase anterior o siguiente.
function onKeydown(event: KeyboardEvent) {
  if (!canControl.value || isTypingOrPressingControl(event.target)) return;
  if (event.code === 'Space') {
    event.preventDefault();
    $voice.toggle();
  } else if (event.code === 'ArrowLeft') {
    event.preventDefault();
    $voice.previous();
  } else if (event.code === 'ArrowRight') {
    event.preventDefault();
    $voice.next();
  }
}

function isTypingOrPressingControl(target: EventTarget | null) {
  if (!(target instanceof HTMLElement)) return false;
  return (
    target.isContentEditable ||
    ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON', 'A'].includes(target.tagName) ||
    ['slider', 'combobox', 'option'].includes(target.getAttribute('role') ?? '')
  );
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown);
  void $voice.loadVoices();
});
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown));
</script>

<template>
  <section
    aria-label="Lectura en vivo"
    class="sticky bottom-0 z-10 border-t border-default bg-default/92 backdrop-blur"
  >
    <div class="mx-auto flex max-w-4xl flex-col gap-3 px-5 py-3 sm:px-12">
      <!-- Subtítulo en vivo: lo que se está diciendo ahora mismo. -->
      <p
        v-if="voice.segmentText"
        class="line-clamp-2 text-base leading-snug text-toned"
        aria-hidden="true"
      >
        {{ caption.before
        }}<mark
          v-if="caption.word"
          class="rounded-sm bg-primary/30 px-0.5 text-highlighted"
          >{{ caption.word }}</mark
        >{{ caption.after }}
      </p>

      <div class="flex flex-wrap items-center gap-2 sm:flex-nowrap">
        <div class="flex items-center gap-1">
          <UButton
            icon="i-lucide-skip-back"
            aria-label="Frase anterior"
            color="neutral"
            variant="ghost"
            :disabled="!canControl"
            @click="$voice.previous()"
          />
          <UButton
            :icon="isSpeaking ? 'i-lucide-pause' : 'i-lucide-play'"
            :aria-label="isSpeaking ? 'Pausar' : 'Continuar'"
            :loading="voice.status === 'starting'"
            :disabled="!canControl"
            size="lg"
            class="rounded-full"
            @click="$voice.toggle()"
          />
          <UButton
            icon="i-lucide-skip-forward"
            aria-label="Frase siguiente"
            color="neutral"
            variant="ghost"
            :disabled="!canControl"
            @click="$voice.next()"
          />
          <UButton
            icon="i-lucide-rotate-ccw"
            aria-label="Volver al inicio"
            color="neutral"
            variant="ghost"
            :disabled="!canControl"
            @click="$voice.restart()"
          />
        </div>

        <div class="flex min-w-40 flex-1 flex-col gap-1.5">
          <div class="flex items-center justify-between gap-2 text-xs">
            <p
              role="status"
              class="flex items-center gap-1.5 truncate"
              :class="voice.status === 'error' ? 'text-error' : 'text-muted'"
            >
              <span
                v-if="isSpeaking"
                aria-hidden="true"
                class="size-1.5 animate-pulse rounded-full bg-primary motion-reduce:animate-none"
              />
              {{ statusText }}
            </p>
            <span
              v-if="voice.segmentCount"
              class="shrink-0 text-dimmed tabular-nums"
            >
              {{ progressText }}
            </span>
          </div>
          <USlider
            :model-value="voice.segmentIndex"
            :max="Math.max(voice.segmentCount - 1, 1)"
            :step="1"
            size="sm"
            :disabled="!canControl"
            aria-label="Ir a una frase"
            @update:model-value="onJump"
          />
        </div>

        <USelect
          v-if="voiceItems.length"
          :model-value="selectedVoice"
          :items="voiceItems"
          icon="i-lucide-mic-vocal"
          size="sm"
          class="w-48"
          aria-label="Voz"
          @update:model-value="$voice.setVoice($event)"
        />
        <USelect
          :model-value="$voice.preferences.value.rate"
          :items="RATE_ITEMS"
          size="sm"
          class="w-20"
          aria-label="Velocidad"
          @update:model-value="$voice.setRate($event)"
        />
      </div>
    </div>
  </section>
</template>
