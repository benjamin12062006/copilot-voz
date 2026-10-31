export type DocumentFormat = 'markdown' | 'text';

/** `agent`: enviado desde Codex o Claude Code por el MCP de la app. */
export type DocumentOrigin = 'web' | 'agent';

export interface DocumentSummary {
  id: string;
  title: string;
  format: DocumentFormat;
  origin: DocumentOrigin;
  /** Aumenta con cada guardado; protege de sobrescribir cambios ajenos. */
  revision: number;
  updatedAt: string;
  wordCount: number;
}

export interface VoiceDocument extends DocumentSummary {
  /** Texto original tal como se guardó. */
  content: string;
}

export interface DocumentDraft {
  title: string;
  format: DocumentFormat;
  content: string;
}

/** Bloques ya preparados por la API. La interfaz los pinta como texto, nunca como HTML. */
export type ReadingBlock =
  | { kind: 'heading'; level: number; text: string }
  | { kind: 'paragraph'; text: string }
  | { kind: 'list'; ordered: boolean; items: string[] }
  | { kind: 'quote'; text: string }
  | { kind: 'code'; language: string | null; text: string }
  | { kind: 'table'; header: string[]; rows: string[][] };

/** Una frase (o trozo de frase larga) que se lee de una vez. */
export interface SpokenSegment {
  /** Bloque de `blocks` al que pertenece, para resaltarlo mientras suena. */
  blockIndex: number;
  text: string;
}

export interface PreparedDocument {
  blocks: ReadingBlock[];
  /** Lo que se leerá en voz alta, en orden: sin código ni marcas de formato. */
  segments: SpokenSegment[];
  /** Avisos para la persona, p. ej. «1 bloque de código no se lee». */
  notices: string[];
}

export type DocumentFailureKind =
  'notFound' | 'conflict' | 'tooLarge' | 'invalid' | 'network';

export class DocumentFailure extends Error {
  constructor(
    message: string,
    public readonly kind: DocumentFailureKind,
  ) {
    super(message);
    this.name = 'DocumentFailure';
  }
}

export interface DocumentService {
  list(): Promise<DocumentSummary[]>;
  get(id: string): Promise<VoiceDocument>;
  create(draft: DocumentDraft): Promise<VoiceDocument>;
  remove(id: string, revision: number): Promise<void>;
  /** Falla con `conflict` si `revision` ya no es la última guardada. */
  update(
    id: string,
    draft: DocumentDraft,
    revision: number,
  ): Promise<VoiceDocument>;
}

/** Mismo límite que COPILOT_STORAGE_MAX_DOCUMENT_BYTES en la API. */
export const MAX_DOCUMENT_BYTES = 1_048_576;
