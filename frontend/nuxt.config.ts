// La clave se lee de .env.local (los scripts pasan --dotenv). Sin clave, el
// módulo Clerk no se registra y la app muestra cómo configurarlo.
const clerkConfigured = Boolean(process.env.NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

export default defineNuxtConfig({
  compatibilityDate: '2026-10-19',
  devtools: { enabled: false },
  modules: [
    '@nuxt/eslint',
    '@nuxt/ui',
    ...(clerkConfigured ? ['@clerk/nuxt'] : []),
  ],
  css: ['~/assets/css/main.css'],
  typescript: { strict: true },
  ui: {
    // Tipografía del sistema, como la referencia macOS; sin descargas en build.
    fonts: false,
  },
  colorMode: { preference: 'dark', fallback: 'dark' },
  icon: {
    // Lucide viene de @iconify-json/lucide: los iconos usados van en el bundle.
    clientBundle: { scan: true },
  },
  runtimeConfig: {
    public: {
      apiBaseUrl: 'http://127.0.0.1:8000/api/v1',
      // Datos reales por defecto; mock queda para vista previa explícita.
      dataSource: 'api',
      // Solo en `pnpm dev:preview`: entra sin Clerk para revisar el diseño.
      previewSession: false,
      clerk: { publishableKey: '' },
    },
  },
  app: {
    head: {
      htmlAttrs: { lang: 'es' },
      title: 'Copilot',
      meta: [
        {
          name: 'description',
          content: 'Escucha tus documentos con una voz clara.',
        },
        { name: 'theme-color', content: '#362e38' },
        { name: 'robots', content: 'noindex, nofollow' },
      ],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },
});
