<template>
  <div
    class="mx-auto min-h-dvh max-w-[1400px] px-6 py-9 sm:px-10 lg:flex lg:items-center lg:px-20 lg:py-20"
  >
    <a
      href="#contenido"
      class="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:rounded-lg focus:bg-white focus:p-3"
    >
      Saltar al contenido
    </a>
    <div
      class="grid w-full gap-10 lg:grid-cols-[1.15fr_1fr] lg:items-center lg:gap-24 xl:gap-36"
    >
      <aside aria-label="Copilot" class="flex flex-col">
        <BrandLogo />
        <div class="mt-12 lg:mt-20">
          <p class="eyebrow text-ink/70">De la curiosidad a la claridad</p>
          <h2
            class="mt-5 max-w-[490px] text-[clamp(2.6rem,4.2vw,4.15rem)] leading-[1.06] font-semibold tracking-[-0.065em] lg:mt-7"
          >
            Todo empieza<br class="hidden lg:block" />
            con una buena pregunta.
          </h2>
          <p class="mt-6 text-lg leading-[1.75] text-muted lg:mt-8 lg:text-xl">
            Un lugar para tus ideas.<br />
            Una cuenta para hacerlas tuyas.
          </p>
        </div>
        <BrandChart class="mt-12 hidden sm:block lg:mt-14" />
      </aside>
      <main
        id="contenido"
        tabindex="-1"
        class="w-full min-w-0 rounded-[30px] border border-line bg-white p-7 shadow-[0_12px_40px_-24px_rgba(22,60,50,0.12)] outline-none sm:p-9 lg:rounded-[32px] lg:p-9"
      >
        <slot />
      </main>
    </div>
  </div>
</template>
