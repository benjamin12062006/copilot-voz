interface PublicConfiguration {
  apiBaseUrl: string;
  clerk?: { publishableKey?: string };
}

export function configurationProblem(
  config: PublicConfiguration,
): string | undefined {
  if (!config.clerk?.publishableKey?.trim()) {
    return 'Configura la clave publicable de Clerk para habilitar el acceso.';
  }
  try {
    const api = new URL(config.apiBaseUrl);
    const local = ['localhost', '127.0.0.1'].includes(api.hostname);
    if (
      api.username ||
      api.password ||
      api.search ||
      api.hash ||
      !(api.protocol === 'https:' || (api.protocol === 'http:' && local)) ||
      !api.pathname.endsWith('/api/v1')
    ) {
      return 'La dirección de conexión de este entorno no es válida.';
    }
  } catch {
    return 'La dirección de conexión de este entorno no es válida.';
  }
}
