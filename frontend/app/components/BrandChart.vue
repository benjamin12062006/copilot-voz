<script setup lang="ts">
const bars = [28, 48, 38, 76, 100, 86, 124];
const colors = [
  '#dfe2da',
  '#cfd6ce',
  '#bfc9c0',
  '#aebcb2',
  '#9aaa9f',
  '#8b9e93',
  '#dd865b',
];
</script>

<template>
  <svg
    viewBox="0 0 232 130"
    aria-hidden="true"
    class="h-auto w-52 lg:w-[252px]"
  >
    <rect
      v-for="(height, index) in bars"
      :key="index"
      :x="index * 34"
      :y="130 - height"
      width="22"
      :height="height"
      rx="6"
      :fill="colors[index]"
    />
  </svg>
</template>
