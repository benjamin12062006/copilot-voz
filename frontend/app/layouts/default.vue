<!-- Layout de acceso: una ventana Focus centrada sobre el color del lateral. -->
<template>
  <div class="flex min-h-dvh items-center justify-center bg-muted p-4 sm:p-8">
    <a
      href="#contenido"
      class="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:rounded-md focus:bg-default focus:p-3"
    >
      Saltar al contenido
    </a>
    <main
      id="contenido"
      tabindex="-1"
      class="w-full max-w-md overflow-hidden rounded-2xl bg-default shadow-2xl ring-1 ring-black/10 outline-none"
    >
      <FocusCover compact />
      <div class="px-7 pt-7 pb-8 sm:px-9">
        <slot />
      </div>
    </main>
  </div>
</template>
