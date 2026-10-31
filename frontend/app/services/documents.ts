import { ApiFailure, type ApiClient } from './api-client';
import {
  DocumentFailure,
  type DocumentService,
  type VoiceDocument,
  type DocumentSummary,
} from '../types/documents';

export function createDocumentService(api: ApiClient): DocumentService {
  async function request<T>(
    path: string,
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE',
    body?: Record<string, unknown>,
  ): Promise<T> {
    try {
      return await api.request<T>(path, method, body);
    } catch (error) {
      if (!(error instanceof ApiFailure)) throw error;
      if (error.status === 404)
        throw new DocumentFailure(error.message, 'notFound');
      if (error.status === 409)
        throw new DocumentFailure(error.message, 'conflict');
      if (error.status === 413)
        throw new DocumentFailure(error.message, 'tooLarge');
      if (error.status === 422)
        throw new DocumentFailure(error.message, 'invalid');
      throw new DocumentFailure(error.message, 'network');
    }
  }
  return {
    async list() {
      return (await request<{ items: DocumentSummary[] }>('/documents')).items;
    },
    async get(id) {
      return (
        await request<{ document: VoiceDocument }>(
          `/documents/${encodeURIComponent(id)}`,
        )
      ).document;
    },
    async create(draft) {
      return (
        await request<{ document: VoiceDocument }>('/documents', 'POST', {
          ...draft,
        })
      ).document;
    },
    async update(id, draft, revision) {
      return (
        await request<{ document: VoiceDocument }>(
          `/documents/${encodeURIComponent(id)}`,
          'PUT',
          { ...draft, revision },
        )
      ).document;
    },
    async remove(id, revision) {
      await request(
        `/documents/${encodeURIComponent(id)}?revision=${revision}`,
        'DELETE',
      );
    },
  };
}
