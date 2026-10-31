export type LiveVoiceStatus =
  | 'idle'
  | 'starting'
  | 'speaking'
  | 'paused'
  | 'ended'
  | 'error'
  | 'unsupported';

export interface LiveVoiceState {
  status: LiveVoiceStatus;
  /** Documento que se está leyendo; null si no hay lectura. */
  documentId: string | null;
  title: string;
  segmentIndex: number;
  segmentCount: number;
  /** Bloque del documento al que pertenece la frase actual. */
  blockIndex: number | null;
  segmentText: string;
  /** Palabra que suena ahora dentro de `segmentText`, si el navegador lo informa. */
  wordStart: number | null;
  wordLength: number;
  message: string | null;
}

export interface VoiceOption {
  /** Nombre de la voz del sistema, p. ej. «Mónica». */
  name: string;
  label: string;
}

export interface VoicePreferences {
  voiceName: string | null;
  rate: number;
}
