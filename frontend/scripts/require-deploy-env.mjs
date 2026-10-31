const publishableKey = process.env.NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY;

if (!publishableKey?.trim()) {
  console.error(
    'Falta NUXT_PUBLIC_CLERK_PUBLISHABLE_KEY para compilar el frontend.',
  );
  process.exit(1);
}

if (process.env.NUXT_PUBLIC_PREVIEW_SESSION === 'true') {
  console.error('Desactiva NUXT_PUBLIC_PREVIEW_SESSION antes de desplegar.');
  process.exit(1);
}

if (!hasPublicApiUrl(process.env.NUXT_PUBLIC_API_BASE_URL)) {
  console.error(
    'NUXT_PUBLIC_API_BASE_URL debe ser la URL HTTPS del backend con /api/v1.',
  );
  process.exit(1);
}

function hasPublicApiUrl(value) {
  try {
    const url = new URL(value);
    const isLocalHost = ['localhost', '127.0.0.1', '::1', '[::1]'].includes(
      url.hostname,
    );
    return (
      url.protocol === 'https:' &&
      !isLocalHost &&
      !url.username &&
      !url.password &&
      !url.search &&
      !url.hash &&
      url.pathname === '/api/v1'
    );
  } catch {
    return false;
  }
}
