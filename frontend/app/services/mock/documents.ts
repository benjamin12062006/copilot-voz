import {
  DocumentFailure,
  MAX_DOCUMENT_BYTES,
  type DocumentDraft,
  type DocumentService,
  type DocumentSummary,
  type VoiceDocument,
} from '../../types/documents';
import { simulateLatency } from './latency';
import { SAMPLE_DOCUMENTS } from './sample-documents';

// Se guarda en este navegador para que crear → recargar se pueda probar.
// No es el almacén real: los documentos de verdad vivirán en Blob (API 03).
const STORAGE_KEY = 'copilot.mock.documents.v1';

const LATENCY_MS = { read: 350, write: 600 };

const DAY_MS = 24 * 60 * 60 * 1000;

export function createSimulatedDocumentService(): DocumentService {
  const documents = loadDocuments();

  async function list(): Promise<DocumentSummary[]> {
    await simulateLatency(LATENCY_MS.read);
    return [...documents.values()]
      .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))
      .map(summaryOf);
  }

  async function get(id: string): Promise<VoiceDocument> {
    await simulateLatency(LATENCY_MS.read);
    return { ...findDocument(id) };
  }

  async function create(draft: DocumentDraft): Promise<VoiceDocument> {
    validateDraft(draft);
    await simulateLatency(LATENCY_MS.write);

    const document = buildDocument(crypto.randomUUID(), draft, 1, 'web');
    documents.set(document.id, document);
    saveDocuments(documents);
    return { ...document };
  }

  async function update(
    id: string,
    draft: DocumentDraft,
    revision: number,
  ): Promise<VoiceDocument> {
    validateDraft(draft);
    await simulateLatency(LATENCY_MS.write);

    const current = findDocument(id);
    if (current.revision !== revision) {
      throw new DocumentFailure(
        'Este documento cambió mientras lo editabas. Tu borrador se conserva.',
        'conflict',
      );
    }
    const document = buildDocument(id, draft, revision + 1, current.origin);
    documents.set(id, document);
    saveDocuments(documents);
    return { ...document };
  }

  function findDocument(id: string): VoiceDocument {
    const document = documents.get(id);
    if (!document) {
      throw new DocumentFailure('Este documento no existe.', 'notFound');
    }
    return document;
  }

  async function remove(id: string, revision: number) {
    const current = findDocument(id);
    if (current.revision !== revision)
      throw new DocumentFailure('El documento cambió. Recárgalo.', 'conflict');
    documents.delete(id);
    saveDocuments(documents);
  }

  return { list, get, create, update, remove };
}

function validateDraft(draft: DocumentDraft) {
  if (!draft.title.trim()) {
    throw new DocumentFailure(
      'Escribe un título para el documento.',
      'invalid',
    );
  }
  if (!draft.content.trim()) {
    throw new DocumentFailure('El documento está vacío.', 'invalid');
  }
  if (new TextEncoder().encode(draft.content).length > MAX_DOCUMENT_BYTES) {
    throw new DocumentFailure(
      'El documento supera el límite de 1 MB.',
      'tooLarge',
    );
  }
}

function buildDocument(
  id: string,
  draft: DocumentDraft,
  revision: number,
  origin: VoiceDocument['origin'],
  updatedAt = new Date().toISOString(),
): VoiceDocument {
  return {
    id,
    title: draft.title.trim(),
    format: draft.format,
    content: draft.content,
    origin,
    revision,
    updatedAt,
    wordCount: countWords(draft.content),
  };
}

function summaryOf({ content: _content, ...summary }: VoiceDocument) {
  return summary;
}

function countWords(content: string) {
  return content.split(/\s+/).filter(Boolean).length;
}

function loadDocuments(): Map<string, VoiceDocument> {
  const saved = readSavedDocuments();
  const documents = saved ?? sampleDocuments();
  return new Map(documents.map((document) => [document.id, document]));
}

function sampleDocuments(): VoiceDocument[] {
  const now = Date.now();
  return SAMPLE_DOCUMENTS.map((sample, index) =>
    buildDocument(
      `muestra-${index + 1}`,
      sample,
      1,
      sample.origin,
      new Date(now - sample.daysAgo * DAY_MS - index * 60_000).toISOString(),
    ),
  );
}

function readSavedDocuments(): VoiceDocument[] | null {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return null;
    const parsed: unknown = JSON.parse(saved);
    return Array.isArray(parsed) && parsed.every(isVoiceDocument)
      ? parsed
      : null;
  } catch {
    return null;
  }
}

function saveDocuments(documents: Map<string, VoiceDocument>) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...documents.values()]));
  } catch {
    // Sin almacenamiento (modo privado): la simulación sigue en memoria.
  }
}

function isVoiceDocument(value: unknown): value is VoiceDocument {
  if (typeof value !== 'object' || value === null) return false;
  const record: Record<string, unknown> = { ...value };
  return (
    typeof record.id === 'string' &&
    typeof record.title === 'string' &&
    typeof record.content === 'string' &&
    (record.format === 'markdown' || record.format === 'text') &&
    (record.origin === 'web' || record.origin === 'agent') &&
    typeof record.revision === 'number' &&
    typeof record.updatedAt === 'string' &&
    typeof record.wordCount === 'number'
  );
}
