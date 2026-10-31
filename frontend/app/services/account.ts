import type { AutoReadMode } from '../types/voice';
import type { ApiClient } from './api-client';

export interface AgentToken {
  id: string;
  name: string;
  createdAt: string;
  expiresAt: string;
  revokedAt: string | null;
  scope: string;
}
export interface IssuedToken extends Omit<AgentToken, 'revokedAt'> {
  token: string;
}
export interface StoragePreference {
  retentionLimit: number;
}
export interface VoicePreference {
  autoReadMode: AutoReadMode;
}

export function createAccountService(api: ApiClient) {
  return {
    async tokens() {
      return (await api.request<{ items: AgentToken[] }>('/mcp/tokens')).items;
    },
    issue(name: string) {
      return api.request<IssuedToken>('/mcp/tokens', 'POST', { name });
    },
    async revoke(id: string) {
      await api.request(`/mcp/tokens/${encodeURIComponent(id)}`, 'DELETE');
    },
    preferences() {
      return api.request<StoragePreference>('/storage/preferences');
    },
    setRetention(retentionLimit: number) {
      return api.request<StoragePreference>('/storage/preferences', 'PUT', {
        retentionLimit,
      });
    },
    voicePreferences() {
      return api.request<VoicePreference>('/voice/preferences');
    },
    setAutoReadMode(autoReadMode: AutoReadMode) {
      return api.request<VoicePreference>('/voice/preferences', 'PUT', {
        autoReadMode,
      });
    },
  };
}
