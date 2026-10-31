/**
 * Convierte un documento en lo que se ve (bloques) y lo que se oye (frases).
 *
 * Reglas de voz tomadas de voz-skill: texto plano y natural, sin código, sin
 * marcas de Markdown, sin URLs largas ni emojis. Cada frase recuerda su bloque
 * para poder resaltarlo mientras suena.
 */
import { marked, type Token, type Tokens } from 'marked';
import type {
  DocumentFormat,
  PreparedDocument,
  ReadingBlock,
  SpokenSegment,
} from '../../types/documents';

/**
 * Una frase más larga se parte por comas: los sintetizadores cortan o
 * aceleran los textos muy largos (curso SwiftUI, «Dividir String en fragmentos»).
 */
const MAX_SEGMENT_CHARS = 240;

const EMOJI = /[\p{Extended_Pictographic}️‍]/gu;

const sentenceSegmenter =
  typeof Intl.Segmenter === 'function'
    ? new Intl.Segmenter('es', { granularity: 'sentence' })
    : null;

export function prepareReading(
  format: DocumentFormat,
  content: string,
): PreparedDocument {
  const reading = new Reading();
  if (format === 'markdown') {
    addMarkdown(reading, content);
  } else {
    addPlainText(reading, content);
  }
  return reading.result();
}

/** Acumula bloques y frases a la vez, para que cada frase sepa su bloque. */
class Reading {
  private blocks: ReadingBlock[] = [];
  private segments: SpokenSegment[] = [];
  private silentCode = 0;
  private skippedHtml = 0;

  /** Añade un bloque visible y lo que se dirá de él, frase a frase. */
  addSpoken(block: ReadingBlock, spokenParts: string[]) {
    const blockIndex = this.blocks.push(block) - 1;
    for (const part of spokenParts) {
      for (const text of speakableChunks(part)) {
        this.segments.push({ blockIndex, text });
      }
    }
  }

  /** Bloque que se ve pero no se lee, como el código. */
  addSilentCode(block: ReadingBlock) {
    this.blocks.push(block);
    this.silentCode++;
  }

  skipHtml() {
    this.skippedHtml++;
  }

  result(): PreparedDocument {
    return {
      blocks: this.blocks,
      segments: this.segments,
      notices: this.notices(),
    };
  }

  private notices() {
    const notices = [];
    if (this.silentCode > 0) {
      notices.push(
        `${this.silentCode} bloque(s) de código se muestran pero no se leen en voz alta.`,
      );
    }
    if (this.skippedHtml > 0) {
      notices.push(
        `${this.skippedHtml} fragmento(s) HTML se omitieron por seguridad.`,
      );
    }
    return notices;
  }
}

function addPlainText(reading: Reading, content: string) {
  const paragraphs = content
    .split(/\n\s*\n/)
    .map((paragraph) => paragraph.replace(/\s+/g, ' ').trim())
    .filter(Boolean);

  for (const text of paragraphs) {
    reading.addSpoken({ kind: 'paragraph', text }, [text]);
  }
}

function addMarkdown(reading: Reading, content: string) {
  for (const token of marked.lexer(content)) {
    addBlockToken(reading, token);
  }
}

function addBlockToken(reading: Reading, token: Token) {
  if (isHeading(token)) {
    const text = inlineText(token.tokens, 'display');
    reading.addSpoken({ kind: 'heading', level: token.depth, text }, [
      withPause(inlineText(token.tokens, 'speech')),
    ]);
  } else if (isParagraph(token)) {
    reading.addSpoken(
      { kind: 'paragraph', text: inlineText(token.tokens, 'display') },
      [inlineText(token.tokens, 'speech')],
    );
  } else if (isList(token)) {
    addList(reading, token);
  } else if (isBlockquote(token)) {
    reading.addSpoken(
      { kind: 'quote', text: inlineText(token.tokens, 'display') },
      [inlineText(token.tokens, 'speech')],
    );
  } else if (isTable(token)) {
    addTable(reading, token);
  } else if (isCode(token)) {
    reading.addSilentCode({
      kind: 'code',
      language: token.lang || null,
      text: token.text,
    });
  } else if (token.type === 'html') {
    reading.skipHtml();
  }
  // `space` y `hr` no se ven ni se leen: solo separan bloques.
}

function addList(reading: Reading, list: Tokens.List) {
  const items = flattenItems(list.items);
  const firstNumber = typeof list.start === 'number' ? list.start : 1;

  // «1: Primero.» y no «1. Primero.»: el separador de frases cortaría tras «1.».
  const spoken = items.map((item, index) => {
    const text = withPause(item.speech);
    return list.ordered ? `${firstNumber + index}: ${text}` : text;
  });

  reading.addSpoken(
    {
      kind: 'list',
      ordered: list.ordered,
      items: items.map((item) => item.display),
    },
    spoken,
  );
}

/** Las sublistas se aplanan: en voz alta no se perciben niveles. */
function flattenItems(items: Tokens.ListItem[]) {
  const flat: { display: string; speech: string }[] = [];
  for (const item of items) {
    const ownTokens = item.tokens.filter((token) => !isList(token));
    flat.push({
      display: inlineText(ownTokens, 'display'),
      speech: inlineText(ownTokens, 'speech'),
    });
    for (const nested of item.tokens.filter(isList)) {
      flat.push(...flattenItems(nested.items));
    }
  }
  return flat.filter((item) => item.display);
}

function addTable(reading: Reading, table: Tokens.Table) {
  const header = table.header.map((cell) => inlineText(cell.tokens, 'display'));
  const rows = table.rows.map((row) =>
    row.map((cell) => inlineText(cell.tokens, 'display')),
  );

  // Una frase por fila: «Elemento: Títulos, ¿Se lee?: Sí.»
  const spoken = table.rows.map((row) =>
    withPause(
      row
        .map(
          (cell, column) =>
            `${header[column]}: ${inlineText(cell.tokens, 'speech')}`,
        )
        .join(', '),
    ),
  );

  reading.addSpoken({ kind: 'table', header, rows }, spoken);
}

/**
 * Texto de los tokens en línea. En `speech` los enlaces que son solo una URL
 * se dicen como «enlace a dominio» y las imágenes por su texto alternativo.
 */
function inlineText(
  tokens: Token[] | undefined,
  mode: 'display' | 'speech',
): string {
  if (!tokens) return '';

  let text = '';
  for (const token of tokens) {
    text += inlineTokenText(token, mode);
  }
  const clean = text.replace(/\s+/g, ' ').trim();
  return mode === 'speech' ? clean.replace(EMOJI, '').trim() : clean;
}

function inlineTokenText(token: Token, mode: 'display' | 'speech'): string {
  if (token.type === 'html') return '';
  if (token.type === 'br' || token.type === 'space') return ' ';
  if (isLink(token)) return linkText(token, mode);
  if (isImage(token)) return imageText(token, mode);
  if ('tokens' in token && Array.isArray(token.tokens)) {
    return inlineText(token.tokens, mode);
  }
  if ('text' in token && typeof token.text === 'string') return token.text;
  return '';
}

function linkText(link: Tokens.Link, mode: 'display' | 'speech') {
  const label = inlineText(link.tokens, mode);
  if (mode === 'display') return label || link.href;
  return looksLikeUrl(label) ? `enlace a ${hostnameOf(link.href)}` : label;
}

function imageText(image: Tokens.Image, mode: 'display' | 'speech') {
  if (!image.text) return '';
  return mode === 'speech' ? `Imagen: ${image.text}.` : image.text;
}

/** Frases listas para la voz; las muy largas se parten por comas. */
function speakableChunks(text: string): string[] {
  const chunks: string[] = [];
  for (const sentence of sentencesOf(text)) {
    if (sentence.length <= MAX_SEGMENT_CHARS) {
      chunks.push(sentence);
    } else {
      chunks.push(...splitAtCommas(sentence));
    }
  }
  return chunks;
}

function sentencesOf(text: string): string[] {
  if (!text.trim()) return [];
  if (!sentenceSegmenter) return [text.trim()];

  const sentences = [];
  for (const { segment } of sentenceSegmenter.segment(text)) {
    const sentence = segment.trim();
    if (sentence) sentences.push(sentence);
  }
  return sentences;
}

function splitAtCommas(sentence: string): string[] {
  const pieces = sentence.split(/(?<=[,;:])\s+/);
  const chunks: string[] = [];
  let current = '';

  for (const piece of pieces) {
    const joined = current ? `${current} ${piece}` : piece;
    if (joined.length > MAX_SEGMENT_CHARS && current) {
      chunks.push(current);
      current = piece;
    } else {
      current = joined;
    }
  }
  if (current) chunks.push(current);
  return chunks;
}

/** Un punto final hace que la voz respire tras títulos y elementos de lista. */
function withPause(text: string) {
  if (!text) return text;
  return /[.!?…:;]$/.test(text) ? text : `${text}.`;
}

function looksLikeUrl(text: string) {
  return /^(https?:\/\/|www\.)\S+$/i.test(text);
}

function hostnameOf(href: string) {
  try {
    return new URL(href).hostname.replace(/^www\./, '');
  } catch {
    return 'una página';
  }
}

function isHeading(token: Token): token is Tokens.Heading {
  return token.type === 'heading';
}

function isParagraph(token: Token): token is Tokens.Paragraph {
  return token.type === 'paragraph';
}

function isList(token: Token): token is Tokens.List {
  return token.type === 'list';
}

function isBlockquote(token: Token): token is Tokens.Blockquote {
  return token.type === 'blockquote';
}

function isTable(token: Token): token is Tokens.Table {
  return token.type === 'table';
}

function isCode(token: Token): token is Tokens.Code {
  return token.type === 'code';
}

function isLink(token: Token): token is Tokens.Link {
  return token.type === 'link';
}

function isImage(token: Token): token is Tokens.Image {
  return token.type === 'image';
}
