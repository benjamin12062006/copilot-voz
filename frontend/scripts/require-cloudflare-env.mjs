const publishableKey = process.env.NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

if (!publishableKey?.trim()) {
  console.error(
    'Falta NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY en las variables de compilación de Cloudflare.',
  );
  process.exit(1);
}

if (process.env.NUXT_PUBLIC_PREVIEW_SESSION === 'true') {
  console.error(
    'Desactiva NUXT_PUBLIC_PREVIEW_SESSION antes de compilar para Cloudflare.',
  );
  process.exit(1);
}
