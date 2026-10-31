/**
 * Lectura en vivo con las voces del sistema (API de voz del navegador a
 * través de easy-speech, que corrige cortes de Chrome en textos largos).
 *
 * Se habla frase a frase: así se puede resaltar lo que suena, saltar de frase
 * y aplicar cambios de voz o velocidad sin esperar al final del documento.
 * Cada lectura, salto o parada cambia `attempt`; una frase cancelada no
 * continúa la lectura antigua.
 */
import EasySpeech from 'easy-speech';
import { readonly, ref } from 'vue';
import type { PreparedDocument, SpokenSegment } from '../types/documents';
import type {
  LiveVoiceState,
  VoiceOption,
  VoicePreferences,
} from '../types/voice';

const PREFERENCES_KEY = 'copilot.voice.preferences.v1';

/** Voces que el usuario ya usaba con VOZ (`say … using "Mónica"`). */
const FAMILIAR_VOICES = ['Mónica', 'Monica', 'Paulina'];
const ENHANCED_VOICE = /premium|mejorada|enhanced|natural|neural/i;

export const SPEECH_RATES = [0.8, 1, 1.15, 1.3, 1.5];
const DEFAULT_PREFERENCES: VoicePreferences = { voiceName: null, rate: 1 };

const regionNames = new Intl.DisplayNames('es', { type: 'region' });

export function createLiveVoice() {
  const state = ref<LiveVoiceState>(idleState());
  const voices = ref<VoiceOption[]>([]);
  const preferences = ref<VoicePreferences>(loadPreferences());

  let attempt = 0;
  let engine: Promise<boolean> | null = null;
  let engineReady = false;
  let segments: SpokenSegment[] = [];

  /** Empieza a leer un documento, desde el principio o desde una frase. */
  async function read(
    documentId: string,
    title: string,
    prepared: PreparedDocument,
    fromSegment = 0,
  ) {
    stop();
    if (prepared.segments.length === 0) return;

    const current = attempt;
    segments = prepared.segments;
    state.value = {
      ...idleState(),
      status: 'starting',
      documentId,
      title,
      segmentCount: segments.length,
    };

    const available = await prepareEngine();
    if (current !== attempt) return;
    if (!available) {
      state.value = {
        ...state.value,
        status: 'unsupported',
        message: 'Este navegador no puede leer en voz alta.',
      };
      return;
    }
    await speakFrom(fromSegment, current);
  }

  function pause() {
    if (state.value.status !== 'speaking') return;
    EasySpeech.pause();
    state.value.status = 'paused';
  }

  function resume() {
    if (state.value.status !== 'paused') return;
    EasySpeech.resume();
    state.value.status = 'speaking';
  }

  function toggle() {
    const { status, segmentIndex } = state.value;
    if (status === 'speaking') pause();
    else if (status === 'paused') resume();
    else if (status === 'ended') jumpTo(0);
    else if (status === 'error') jumpTo(segmentIndex);
  }

  function restart() {
    jumpTo(0);
  }

  function next() {
    jumpTo(state.value.segmentIndex + 1);
  }

  function previous() {
    jumpTo(state.value.segmentIndex - 1);
  }

  /** Lee desde la frase indicada dentro de la lectura actual. */
  function jumpTo(index: number) {
    if (segments.length === 0 || !engineReady) return;
    const target = Math.min(Math.max(index, 0), segments.length - 1);
    const current = cancelCurrentSpeech();
    void speakFrom(target, current);
  }

  /** Deja de leer: salir de la página, cambiar de documento o de cuenta. */
  function stop() {
    if (engineReady && isActive()) cancelCurrentSpeech();
    else attempt++;
    segments = [];
    state.value = idleState();
  }

  function setVoice(voiceName: string) {
    updatePreferences({ voiceName });
  }

  function setRate(rate: number) {
    updatePreferences({ rate });
  }

  /** Carga la lista de voces sin empezar a hablar (para el selector). */
  async function loadVoices() {
    await prepareEngine();
  }

  async function speakFrom(index: number, current: number) {
    for (let position = index; position < segments.length; position++) {
      showSegment(position);
      const completed = await speakSegment(segments[position]!, current);
      if (!completed) return;
    }
    if (current === attempt) state.value.status = 'ended';
  }

  /** true si la frase terminó; false si se canceló (salto o parada) o falló. */
  async function speakSegment(segment: SpokenSegment, current: number) {
    try {
      await EasySpeech.speak({
        text: segment.text,
        voice: selectedVoice(),
        rate: preferences.value.rate,
        pitch: 1,
        volume: 1,
        boundary: (event) => markWord(event, segment.text, current),
      });
      return current === attempt;
    } catch {
      // Cancelar una frase también la rechaza: solo es fallo si sigue vigente.
      if (current === attempt) {
        fail('La voz se interrumpió. Pulsa reproducir para seguir.');
      }
      return false;
    }
  }

  function showSegment(index: number) {
    const segment = segments[index]!;
    state.value = {
      ...state.value,
      status: state.value.status === 'paused' ? 'paused' : 'speaking',
      segmentIndex: index,
      blockIndex: segment.blockIndex,
      segmentText: segment.text,
      wordStart: null,
      wordLength: 0,
      message: null,
    };
  }

  function markWord(
    event: SpeechSynthesisEvent,
    text: string,
    current: number,
  ) {
    if (current !== attempt || event.name === 'sentence') return;
    state.value.wordStart = event.charIndex;
    state.value.wordLength =
      event.charLength || wordLengthAt(text, event.charIndex);
  }

  /**
   * Cancela la frase en curso y devuelve el nuevo intento. Si estaba en pausa,
   * se reanuda el sintetizador: Chrome no habla de nuevo mientras sigue pausado.
   */
  function cancelCurrentSpeech() {
    const wasPaused = state.value.status === 'paused';
    attempt++;
    EasySpeech.cancel();
    if (wasPaused) {
      EasySpeech.resume();
      state.value.status = 'speaking';
    }
    return attempt;
  }

  function updatePreferences(changes: Partial<VoicePreferences>) {
    preferences.value = { ...preferences.value, ...changes };
    savePreferences(preferences.value);
    // Mientras habla, la frase actual se repite con la voz o velocidad nueva.
    if (state.value.status === 'speaking') jumpTo(state.value.segmentIndex);
  }

  function prepareEngine() {
    engine ??= startEngine();
    return engine;
  }

  async function startEngine() {
    if (!EasySpeech.detect().speechSynthesis) return false;
    try {
      await EasySpeech.init({ maxTimeout: 5000, interval: 250, quiet: true });
    } catch {
      return false;
    }
    engineReady = true;
    voices.value = spanishVoices().map(voiceOption);
    return true;
  }

  function selectedVoice(): SpeechSynthesisVoice | undefined {
    const available = spanishVoices();
    const preferred = available.find(
      (voice) => voice.name === preferences.value.voiceName,
    );
    return preferred ?? available[0];
  }

  function isActive() {
    return ['starting', 'speaking', 'paused'].includes(state.value.status);
  }

  function fail(message: string) {
    state.value = { ...state.value, status: 'error', message };
  }

  return {
    state: readonly(state),
    voices: readonly(voices),
    preferences: readonly(preferences),
    read,
    pause,
    resume,
    toggle,
    restart,
    next,
    previous,
    jumpTo,
    stop,
    setVoice,
    setRate,
    loadVoices,
  };
}

export type LiveVoice = ReturnType<typeof createLiveVoice>;

/**
 * Voces en español, de la más probable a gustar a la menos: las de VOZ,
 * las mejoradas del sistema, las locales y después el resto (curso SwiftUI,
 * «Voz por idioma»: una voz de otro idioma lee mal el español).
 */
function spanishVoices(): SpeechSynthesisVoice[] {
  return EasySpeech.voices()
    .filter((voice) => voice.lang.toLowerCase().startsWith('es'))
    .sort(
      (a, b) => voiceRank(a) - voiceRank(b) || a.name.localeCompare(b.name),
    );
}

function voiceRank(voice: SpeechSynthesisVoice) {
  if (FAMILIAR_VOICES.some((name) => voice.name.startsWith(name))) return 0;
  if (ENHANCED_VOICE.test(voice.name)) return 1;
  if (voice.localService) return 2;
  return 3;
}

function voiceOption(voice: SpeechSynthesisVoice): VoiceOption {
  const region = voice.lang.split(/[-_]/)[1]?.toUpperCase();
  const regionName = region ? regionNames.of(region) : null;
  return {
    name: voice.name,
    label: regionName ? `${voice.name} · ${regionName}` : voice.name,
  };
}

function wordLengthAt(text: string, index: number) {
  const match = /^[\p{L}\p{N}'’-]+/u.exec(text.slice(index));
  return match?.[0].length ?? 0;
}

function idleState(): LiveVoiceState {
  return {
    status: 'idle',
    documentId: null,
    title: '',
    segmentIndex: 0,
    segmentCount: 0,
    blockIndex: null,
    segmentText: '',
    wordStart: null,
    wordLength: 0,
    message: null,
  };
}

/** Preferencia de este navegador: si no se puede leer, se usan las de serie. */
function loadPreferences(): VoicePreferences {
  try {
    const saved: unknown = JSON.parse(
      localStorage.getItem(PREFERENCES_KEY) ?? 'null',
    );
    return isVoicePreferences(saved) ? saved : { ...DEFAULT_PREFERENCES };
  } catch {
    return { ...DEFAULT_PREFERENCES };
  }
}

function savePreferences(preferences: VoicePreferences) {
  try {
    localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences));
  } catch {
    // Sin almacenamiento la preferencia dura hasta recargar.
  }
}

function isVoicePreferences(value: unknown): value is VoicePreferences {
  if (typeof value !== 'object' || value === null) return false;
  const record: Record<string, unknown> = { ...value };
  return (
    (record.voiceName === null || typeof record.voiceName === 'string') &&
    typeof record.rate === 'number' &&
    SPEECH_RATES.includes(record.rate)
  );
}
