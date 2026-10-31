<script setup lang="ts">
/**
 * Cabecera ilustrada propia, inspirada en la referencia Focus: bandas de color
 * y curvas superpuestas. No reutiliza la imagen original.
 */
withDefaults(defineProps<{ compact?: boolean }>(), { compact: false });
</script>

<template>
  <div
    class="relative w-full shrink-0 overflow-hidden"
    :class="compact ? 'h-24 sm:h-28' : 'h-36 sm:h-44'"
  >
    <svg
      class="absolute inset-0 size-full"
      viewBox="0 0 1200 300"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="cover-bands" x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stop-color="var(--color-cover-sage)" />
          <stop offset="0.1" stop-color="var(--color-cover-mustard)" />
          <stop offset="0.24" stop-color="var(--color-cover-mauve)" />
          <stop offset="0.4" stop-color="var(--color-cover-lavender)" />
          <stop offset="0.5" stop-color="var(--color-cover-navy)" />
          <stop offset="0.6" stop-color="var(--color-cover-blue)" />
          <stop offset="0.76" stop-color="var(--color-cover-peach)" />
          <stop offset="0.9" stop-color="var(--color-cover-orange)" />
          <stop offset="1" stop-color="var(--color-cover-red)" />
        </linearGradient>
        <linearGradient id="cover-glass" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stop-color="#ffffff" stop-opacity="0.35" />
          <stop offset="1" stop-color="#ffffff" stop-opacity="0.04" />
        </linearGradient>
        <linearGradient id="cover-wave" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stop-color="var(--color-cover-blue)" />
          <stop offset="1" stop-color="#1f5f99" />
        </linearGradient>
      </defs>

      <rect width="1200" height="300" fill="url(#cover-bands)" />

      <!-- Panel rosado translúcido con esquinas redondeadas, arriba a la izquierda. -->
      <rect
        x="330"
        y="-60"
        width="300"
        height="230"
        rx="70"
        fill="var(--color-cover-mauve)"
        opacity="0.85"
      />
      <rect
        x="330"
        y="-60"
        width="300"
        height="230"
        rx="70"
        fill="url(#cover-glass)"
      />

      <!-- Curva azul que baja y vuelve a subir, como una «S» tumbada. -->
      <path
        d="M300 300 C 360 170, 470 150, 560 190 S 700 300, 760 210 S 860 40, 980 70 L 980 300 Z"
        fill="url(#cover-wave)"
        opacity="0.92"
      />

      <!-- Lavanda y marino superpuestos en el centro. -->
      <path
        d="M560 -20 C 640 40, 640 160, 720 200 L 720 -20 Z"
        fill="var(--color-cover-lavender)"
        opacity="0.75"
      />
      <path
        d="M660 300 C 680 210, 760 170, 820 190 L 820 300 Z"
        fill="var(--color-cover-navy)"
        opacity="0.9"
      />

      <!-- Bloque melocotón con borde redondeado a la derecha. -->
      <rect
        x="860"
        y="40"
        width="220"
        height="320"
        rx="90"
        fill="var(--color-cover-peach)"
        opacity="0.8"
      />
      <path
        d="M1010 300 C 1040 200, 1110 150, 1200 140 L 1200 300 Z"
        fill="var(--color-cover-orange)"
        opacity="0.95"
      />

      <!-- Brillos verticales que dan el efecto de vidrio de la referencia. -->
      <rect x="220" y="0" width="70" height="300" fill="url(#cover-glass)" />
      <rect x="780" y="0" width="40" height="300" fill="url(#cover-glass)" />
      <rect x="1090" y="0" width="60" height="300" fill="url(#cover-glass)" />
    </svg>

    <div
      class="absolute inset-x-0 top-0 flex items-center justify-between gap-2 p-3"
    >
      <slot name="leading" />
      <div class="ms-auto flex items-center gap-1">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>
