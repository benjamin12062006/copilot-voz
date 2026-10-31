import { createDocumentService } from '../services/documents';
import { createLiveVoice } from '../services/live-voice';
import { createSimulatedDocumentService } from '../services/mock/documents';
import type { DocumentService } from '../types/documents';
import type { AccessState } from '../types/access';

/**
 * Documentos (simulados hasta API 03) y voz en vivo con las voces del sistema.
 */
export default defineNuxtPlugin({
  name: 'copilot-voice',
  dependsOn: ['copilot-access', 'copilot-api'],
  setup(): {
    provide: {
      documents: DocumentService;
      voice: ReturnType<typeof createLiveVoice>;
    };
  } {
    const { $api, $accessProvider } = useNuxtApp();
    const config = useRuntimeConfig().public;
    const documents =
      config.dataSource === 'api' && $accessProvider !== 'preview'
        ? createDocumentService($api)
        : createSimulatedDocumentService();
    const voice = createLiveVoice();

    // Salir de la cuenta detiene la lectura.
    const access = useState<AccessState>('access');
    watch(
      () => access.value.status,
      (status) => {
        if (status !== 'ready') voice.stop();
      },
    );

    return { provide: { documents, voice } };
  },
});
