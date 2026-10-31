# 05 — Voz en vivo de la redacción Markdown

Fecha de creación: 2026-10-31
Estado: Plan
Ámbito: frontend Nuxt, voz
Relacionada con: [fuentes de voz en vivo](../../fonts/frontend/03-voz-en-vivo-navegador.md), [plan 04 del lector](04-lector-y-reproductor.md) (lo sustituye en la parte de voz), [bitácora frontend 01](../../../bitacora-construccion/frontend/01-pantallas-focus-nuxt-ui-y-clerk.md)

## Objetivo

Escuchar cualquier documento leído en voz alta en el momento, en español, como hace `voz-skill` con sus redacciones. El texto que se oye se resalta en pantalla, y se puede pausar, continuar, saltar de frase, volver al inicio y empezar desde un bloque concreto.

## Cambio de decisión

El [plan 04](04-lector-y-reproductor.md) suponía audio generado por la API y un WAV silencioso mientras tanto. A petición del usuario, la voz la produce ahora el navegador (API de voz + `easy-speech`). La preparación del Markdown para leer pasa a ser código real del frontend (`services/reading/`) y deja de ser parte del simulador. El audio de API 04 queda como opción futura, no como requisito de esta pantalla.

## Reglas de lectura

Tomadas del «Formato de voz» de `voz-skill`: texto plano, sin código, rutas ni marcas.

- Encabezados, párrafos, citas y elementos de lista se leen. Cada frase es un fragmento, separado con `Intl.Segmenter('es')`; las frases muy largas se parten por comas (curso C1).
- Tablas: una frase por fila, «columna: valor».
- Bloques de código y HTML: se muestran y no se leen, con aviso.
- Enlaces: se lee su texto. Una URL sola se lee como «enlace a dominio». Imágenes: «Imagen: texto alternativo». Emojis: se omiten.

## Incrementos

1. `prepareReading`: bloques + fragmentos hablados con el índice de su bloque.
2. `createLiveVoice` sobre `easy-speech`: voces en español (preferencia guardada → Mónica/Paulina → mejoradas → locales), velocidad, estados y descarte de intentos cancelados.
3. Barra «Lectura en vivo» con la frase actual y la palabra resaltada, controles, selector de voz y velocidad, y teclado (Espacio, ← →).
4. Bloque actual resaltado y con desplazamiento automático; clic en un bloque para leer desde ahí.
5. Retirar el WAV simulado y `createVoicePlayer`.

## Comprobación prevista

Typecheck, lint, build. En el navegador: voces españolas detectadas, lectura que avanza de frase en frase con resaltado, pausa y continuación, saltos, velocidad aplicada en la frase siguiente y lectura detenida al salir.
