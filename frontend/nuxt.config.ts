import tailwindcss from '@tailwindcss/vite';

const clerkConfigured = Boolean(process.env.NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY);

export default defineNuxtConfig({
  compatibilityDate: '2026-10-19',
  devtools: { enabled: false },
  modules: ['@nuxt/eslint', ...(clerkConfigured ? ['@clerk/nuxt'] : [])],
  css: ['~/assets/css/main.css'],
  vite: { plugins: [tailwindcss()] },
  typescript: { strict: true },
  runtimeConfig: {
    public: {
      apiBaseUrl: 'http://127.0.0.1:8000/api/v1',
      clerk: { publishableKey: '' },
    },
  },
  app: {
    head: {
      htmlAttrs: { lang: 'es' },
      title: 'Copilot · Tu cuenta',
      meta: [
        {
          name: 'description',
          content: 'Un lugar para tus ideas. Una cuenta para hacerlas tuyas.',
        },
        { name: 'theme-color', content: '#F6F4ED' },
        { name: 'robots', content: 'noindex, nofollow' },
      ],
      link: [{ rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }],
    },
  },
});
