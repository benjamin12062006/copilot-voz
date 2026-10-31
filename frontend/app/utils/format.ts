import type { DocumentFormat } from '../types/documents';

const MINUTE_MS = 60_000;
const HOUR_MS = 60 * MINUTE_MS;
const DAY_MS = 24 * HOUR_MS;

const relativeTime = new Intl.RelativeTimeFormat('es', { numeric: 'auto' });

/** «hace 5 minutos», «ayer», «hace 3 días». */
export function formatRelativeDate(iso: string, now = Date.now()) {
  const elapsed = new Date(iso).getTime() - now;
  if (Math.abs(elapsed) < HOUR_MS) {
    return relativeTime.format(Math.round(elapsed / MINUTE_MS), 'minute');
  }
  if (Math.abs(elapsed) < DAY_MS) {
    return relativeTime.format(Math.round(elapsed / HOUR_MS), 'hour');
  }
  return relativeTime.format(Math.round(elapsed / DAY_MS), 'day');
}

/** Segundos como m:ss, para el progreso del audio. */
export function formatClock(totalSeconds: number) {
  const safeSeconds = Number.isFinite(totalSeconds) ? totalSeconds : 0;
  const minutes = Math.floor(safeSeconds / 60);
  const seconds = Math.floor(safeSeconds % 60);
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

export const FORMAT_LABELS: Record<DocumentFormat, string> = {
  markdown: 'Markdown',
  text: 'Texto',
};

/** Color del punto de cada formato en el lateral, como los «Tags» de Focus. */
export const FORMAT_DOT_CLASSES: Record<DocumentFormat, string> = {
  markdown: 'bg-dot-violet',
  text: 'bg-dot-blue',
};

export function greetingFor(date = new Date()) {
  const hour = date.getHours();
  if (hour < 6) return 'Buenas noches';
  if (hour < 13) return 'Buenos días';
  if (hour < 20) return 'Buenas tardes';
  return 'Buenas noches';
}
