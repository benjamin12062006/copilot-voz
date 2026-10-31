# 04 — Lector Original/Lectura y reproductor único

Fecha de creación: 2026-10-31
Estado: Implementado con datos simulados — [bitácora frontend 01](../../../bitacora-construccion/frontend/01-pantallas-focus-nuxt-ui-y-clerk.md)
Ámbito: frontend Nuxt, voz
Relacionada con: [plan 05 incrementos 4 y 5](../05-frontend-acceso-y-panel-voz.md), [estados de reproducción](../../diagrams/03-estados-de-reproduccion.md), [API 04](../04-api-voz-y-mcp.md)

## Objetivo

Leer un documento en modo Lectura (bloques) u Original (texto literal) y escucharlo con controles reales: reproducir, pausar, continuar, volver al inicio y progreso.

## Decisiones

- Un único `useVoicePlayer` por aplicación, con una sola sesión a la vez (documento, revisión, Object URL y `HTMLAudioElement`) y un contador de intentos para descartar respuestas tardías. Estados: `idle`, `preparing`, `ready`, `playing`, `paused`, `ended`, `error`.
- El audio simulado es un WAV silencioso generado en el navegador, con la duración estimada de la lectura. Así los controles ejercitan el elemento de audio real, igual que con la API. La interfaz indica «Audio simulado» mientras dure.
- Cambiar de documento, salir o cerrar sesión detiene el audio, revoca la URL e invalida el intento.
- Bloques: encabezado, párrafo, lista, cita, código y tabla. El texto se pinta como texto, nunca como HTML.

## Incrementos

1. Tipos de bloques y componente `DocumentBlocks`.
2. `/voice/:id` con `UTabs` Lectura/Original, avisos de preparación y edición.
3. `useVoicePlayer` y barra `VoicePlayerBar` con estado escrito y teclado (espacio para reproducir o pausar).

## Comprobación prevista

En navegador: generar → reproducir → pausar → continuar → reiniciar → fin. Cambiar de documento durante la generación no reproduce el anterior. Además, typecheck, lint y build.
