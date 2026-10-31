<script setup lang="ts">
import type { ReadingBlock } from '../types/documents';

const props = defineProps<{
  blocks: ReadingBlock[];
  /** Bloque que suena ahora; se resalta y se mantiene a la vista. */
  activeBlock: number | null;
  /** Primera frase de cada bloque que se lee (el código no está). */
  firstSegmentOfBlock: Map<number, number>;
}>();

const emit = defineEmits<{ readFrom: [segmentIndex: number] }>();

const root = ref<HTMLElement | null>(null);

// El título de la página ya es h1: los encabezados del documento empiezan en h2.
function headingTag(level: number) {
  return `h${Math.min(level + 1, 6)}`;
}

const HEADING_CLASSES: Record<number, string> = {
  1: 'text-2xl font-light text-highlighted',
  2: 'text-xl font-normal text-highlighted',
  3: 'text-lg font-medium text-highlighted',
};

function headingClass(level: number) {
  return HEADING_CLASSES[level] ?? 'text-base font-semibold text-highlighted';
}

function spacingOf(block: ReadingBlock) {
  return block.kind === 'heading' ? 'mt-7' : 'mt-3';
}

function readFrom(blockIndex: number) {
  const segmentIndex = props.firstSegmentOfBlock.get(blockIndex);
  if (segmentIndex !== undefined) emit('readFrom', segmentIndex);
}

// Mantiene a la vista lo que se está leyendo, sin saltos si ya se ve.
watch(
  () => props.activeBlock,
  async (blockIndex) => {
    if (blockIndex === null) return;
    await nextTick();
    const element = root.value?.querySelector(`[data-block="${blockIndex}"]`);
    if (element instanceof HTMLElement && !isComfortablyVisible(element)) {
      element.scrollIntoView({ block: 'center', behavior: scrollBehavior() });
    }
  },
);

/** Visible y no tapado por la barra de lectura fija de abajo. */
function isComfortablyVisible(element: HTMLElement) {
  const { top, bottom } = element.getBoundingClientRect();
  const BOTTOM_BAR_PX = 160;
  return top >= 0 && bottom <= window.innerHeight - BOTTOM_BAR_PX;
}

function scrollBehavior(): ScrollBehavior {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ? 'auto'
    : 'smooth';
}
</script>

<template>
  <!-- Todo se interpola como texto: un documento nunca inyecta HTML. -->
  <div
    ref="root"
    class="max-w-[68ch] text-[1.0625rem] leading-relaxed text-default"
  >
    <div
      v-for="(block, index) in blocks"
      :key="index"
      :data-block="index"
      class="group relative -mx-3 rounded-lg px-3 py-1 transition-colors duration-300 first:mt-0"
      :class="[
        spacingOf(block),
        index === activeBlock ? 'bg-primary/12 ring-1 ring-primary/25' : '',
      ]"
      :aria-current="index === activeBlock ? 'true' : undefined"
    >
      <UButton
        v-if="firstSegmentOfBlock.has(index)"
        icon="i-lucide-play"
        aria-label="Leer desde aquí"
        color="neutral"
        variant="ghost"
        size="xs"
        class="absolute top-1.5 -left-7 opacity-0 group-hover:opacity-100 focus-visible:opacity-100"
        @click="readFrom(index)"
      />

      <component
        :is="headingTag(block.level)"
        v-if="block.kind === 'heading'"
        :class="headingClass(block.level)"
      >
        {{ block.text }}
      </component>

      <p v-else-if="block.kind === 'paragraph'">
        {{ block.text }}
      </p>

      <component
        :is="block.ordered ? 'ol' : 'ul'"
        v-else-if="block.kind === 'list'"
        class="space-y-1.5 ps-6"
        :class="block.ordered ? 'list-decimal' : 'list-disc'"
      >
        <li
          v-for="(item, itemIndex) in block.items"
          :key="itemIndex"
          class="marker:text-muted"
        >
          {{ item }}
        </li>
      </component>

      <blockquote
        v-else-if="block.kind === 'quote'"
        class="border-s-2 border-primary/60 ps-4 text-toned italic"
      >
        {{ block.text }}
      </blockquote>

      <figure v-else-if="block.kind === 'code'">
        <figcaption class="mb-1 flex items-center gap-1.5 text-xs text-muted">
          <UIcon name="i-lucide-volume-x" class="size-3.5" />
          Código{{ block.language ? ` · ${block.language}` : '' }} · no se lee
          en voz alta
        </figcaption>
        <pre
          class="overflow-x-auto rounded-lg bg-muted p-3 font-mono text-sm leading-normal text-toned"
        ><code>{{ block.text }}</code></pre>
      </figure>

      <div
        v-else-if="block.kind === 'table'"
        class="overflow-x-auto rounded-lg ring-1 ring-(--ui-border)"
      >
        <table class="w-full text-left text-sm">
          <thead class="bg-muted text-toned">
            <tr>
              <th
                v-for="(cell, cellIndex) in block.header"
                :key="cellIndex"
                scope="col"
                class="px-3 py-2 font-medium"
              >
                {{ cell }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, rowIndex) in block.rows"
              :key="rowIndex"
              class="border-t border-default"
            >
              <td
                v-for="(cell, cellIndex) in row"
                :key="cellIndex"
                class="px-3 py-2"
              >
                {{ cell }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
