# 03 — Voz en vivo en el navegador: API de voz, easy-speech y alternativas

Fecha de creación: 2026-10-31
Tipo de fuente: documentación oficial, paquetes instalados, transcripciones de curso y sistema VOZ propio
Fecha de consulta: 2026-10-31
Relacionada con: [plan frontend 05](../../plans/frontend/05-voz-en-vivo.md), [VOZ y filosofía](../04-contrato-voz-y-filosofia.md), [voz Python y MCP](../14-voz-python-y-mcp.md), [Markdown para voz](../08-markdown-pantalla-y-voz.md)

## Necesidad de consulta

El usuario pidió escuchar en vivo la redacción de los Markdown desde Vue/TS, con una biblioteca real, porque eso es lo que persigue `voz-skill`. Hasta ahora la voz era un WAV silencioso simulado.

## Localización verificable

| ID | Fuente | Localizador |
| --- | --- | --- |
| S1 | [MDN · SpeechSynthesis](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis) | Instance methods, `voiceschanged`. Baseline «Widely available» desde 2018. |
| S2 | `easy-speech` 2.4.0 (MIT, sin dependencias, publicado el 2024-09-12), [repositorio](https://github.com/jankapunkt/easy-speech) | `dist/index.d.ts` y `dist/EasySpeech.js`: `init`, `speak`, `cancel`, `pause`, `resume`, `resumeInfinity` |
| S3 | [kokoro.js README](https://github.com/hexgrad/kokoro/blob/main/kokoro.js/README.md) | Voices: solo inglés americano (20) y británico (8). Modelo `onnx-community/Kokoro-82M-v1.0-ONNX` |
| S4 | npm `@mintplex-labs/piper-tts-web` 1.0.5 (MIT; motor Piper) | Descripción del paquete; licencia del motor en la [ficha 14](../14-voz-python-y-mcp.md) (V3) |
| C1 | Curso «SwiftUI y UIKit para iOS», Sección 54 «Lectura con sintetizador de voz y la API Wikipedia (iOS 17)», `481. Dividir String en fragmentos.md`, líneas 13 y 25–29 | Ruta: `Swift/SwiftUI y UIKit para iOS/Sección 54 Lectura con sintetizador de voz y la API Wikipedia ( iOS 17)/` |
| C2 | Misma sección, `482. Voz por idioma.md`, líneas 17–19 | |
| C3 | Misma sección, `479. Botonera para control de voz.md`, líneas 13–19 | |
| V1 | Sistema VOZ propio: `/Users/benji/Documents/VOZ/voice/README.md` y `parar_voz.scpt` | `say … using "Mónica"` / `"Paulina"` |
| V2 | `voz-skill` (`~/.claude/skills/voz-skill/SKILL.md`), «Formato de voz» | Texto plano, sin Markdown ni código, sin rutas ni comandos |

## Evidencia

- **S1:** `speechSynthesis` habla `SpeechSynthesisUtterance` en cola, con `pause`, `resume` y `cancel` y las voces del dispositivo. La lista de voces puede llegar tarde (`voiceschanged`).
- **S2:** `easy-speech` espera a que las voces carguen, por evento o por sondeo, y su `speak` devuelve una promesa que se resuelve al terminar y se rechaza con el evento `error`. Antes de hablar cancela lo anterior. En Chrome de escritorio aplica `resumeInfinity`: pausa y reanuda cada 5 s solo si se está hablando y no hay pausa del usuario, para que los textos largos no se corten.
- **S3:** kokoro-js solo ofrece voces en inglés, así que no sirve para leer en español.
- **C1:** con un texto muy grande «se corta». El curso lo divide en fragmentos y encadena su lectura, y al detener vacía la cola de fragmentos.
- **C2:** cada idioma necesita una voz de ese idioma, porque una voz inglesa lee mal el español. Además, la calidad cambia entre voces del sistema.
- **C3:** la lectura se controla con botones explícitos (leer, detener, volver).
- **V1:** el usuario ya escucha sus redacciones con las voces del sistema de macOS «Mónica» y «Paulina».

## Interpretación y límites

La API del navegador usa las mismas voces del sistema que VOZ (V1). Empieza sin descargas y emite límites de palabra para resaltar en vivo. Su calidad depende del sistema operativo y del navegador; los eventos `boundary` no están garantizados en todas las voces. C1 y C2 son del sintetizador de iOS (AVSpeechSynthesizer): se toman como principio, no como API. El curso divide por comas; aquí se divide por frases con `Intl.Segmenter`, y por comas solo cuando una frase es muy larga.

## Decisión

| Opción | Ventaja | Coste | Decisión |
| --- | --- | --- | --- |
| API del navegador + `easy-speech` | Voces del sistema (las de VOZ), inicio inmediato, pausa real y límites de palabra | Calidad según el sistema | **Elegida** |
| kokoro-js (S3) | Voz neuronal en el navegador | Sin español | Descartada |
| Piper en WASM (S4) | Voces neuronales en español | ~60 MB por voz, carga lenta y licencia GPL del motor por revisar | Pospuesta como mejora futura |
| Audio generado en API 04 | Misma voz en todos los dispositivos | No es en vivo; requiere backend | Se mantiene en el plan de API, fuera de esta pantalla |
