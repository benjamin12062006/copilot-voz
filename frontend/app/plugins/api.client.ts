import { createApiClient, type ApiClient } from '../services/api-client';
import { createAccountService } from '../services/account';

export default defineNuxtPlugin({
  name: 'copilot-api',
  dependsOn: ['copilot-access'],
  setup(): {
    provide: {
      api: ApiClient;
      account: ReturnType<typeof createAccountService>;
    };
  } {
    const { $session } = useNuxtApp();
    const api = createApiClient(useRuntimeConfig().public.apiBaseUrl, $session);
    return { provide: { api, account: createAccountService(api) } };
  },
});
