---
name: voz-redaccion
description: Modo de voz persistente por chat que envía redacciones claras y humanas a la biblioteca de Copilot mediante la herramienta MCP voice_submit_document para escucharlas en la interfaz web. Usar al invocar /voz-redaccion o $voz-redaccion, pedir encender, apagar o consultar información/estado, y también de forma implícita en cada turno posterior del mismo chat mientras el modo siga encendido.
---

# Voz Redacción (Copilot MCP)

## Contexto de la aplicación y arquitectura

- **Interfaz web (Copilot):** El usuario escucha las redacciones en la aplicación web de Copilot (`http://localhost:3000`, estética Focus), que prepara el documento (`prepareReading`), lo segmenta por bloques y frases en español y lo lee en voz alta con las voces del sistema (`easy-speech`) resaltando el bloque y la palabra actual.
- **Transporte y almacenamiento (MCP + FastAPI):** En lugar de crear archivos `.txt` locales en disco o eliminar archivos antiguos manualmente, esta skill utiliza exclusivamente la herramienta MCP `voice_submit_document` del servidor `copilot-voz` (`backend/app/mcp_server.py`), que envía el documento a FastAPI (`POST /api/v1/agent/documents`).
- **Retención y seguridad:** El backend FastAPI, Turso y Upstash Blob gestionan automáticamente el almacenamiento privado por propietario (`origin: "agent"`, sección **«Enviado por agentes»**) y aplican el límite de retención configurado por el usuario en la web (`20` por defecto, `1..100` en **Perfil → Almacenamiento**). El MCP nunca borra documentos ni modifica límites.

## Objetivo

Responder en paralelo cuando el modo esté encendido:
1. Entregar la respuesta normal y completa en el chat.
2. Enviar en ese mismo turno una redacción pensada para ser escuchada en Copilot mediante `voice_submit_document`.

Mantener un modo de voz con estado independiente en cada chat.

## Estados y comandos

Interpretar la invocación explícita de `/voz-redaccion` o `$voz-redaccion` sin subcomando como **encender**.

- **Encendido:** `/voz-redaccion`, `$voz-redaccion`, `/voz-redaccion encender`, `$voz-redaccion encender`, `activar voz`. Activar antes de responder y enviar la redacción mediante `voice_submit_document` en ese mismo turno.
- **Apagado:** `/voz-redaccion apagar`, `$voz-redaccion apagar`, `desactivar voz`. Apagar antes de responder y no invocar `voice_submit_document` en ese turno.
- **Información / Estado:** `/voz-redaccion informacion`, `/voz-redaccion estado`, `$voz-redaccion informacion`, `$voz-redaccion estado`. Informar si el modo está encendido o apagado sin cambiarlo. Si estaba encendido, enviar también la redacción de voz del turno; si estaba apagado, no enviarla.

Resolver el estado actual buscando en el historial del chat la orden de control más reciente. Una activación permanece vigente en todos los turnos posteriores del mismo chat hasta encontrar una orden de apagado. Un chat nuevo comienza apagado hasta que el usuario invoque la skill.

Cuando el estado esté encendido, aplicar esta skill en cada turno posterior aunque el mensaje nuevo trate otro tema y no vuelva a mencionar `/voz-redaccion` ni `$voz-redaccion`. Mantener `policy.allow_implicit_invocation: true` en `agents/openai.yaml` para favorecer esta continuidad.

## Flujo obligatorio cuando está encendido

1. Revisar el contexto de los últimos turnos del chat para mantener continuidad narrativa.
2. Resolver la tarea o consulta del usuario.
3. Redactar el texto para escuchar en Copilot siguiendo las reglas de **Formato de redacción para voz**.
4. Definir un `title` claro y descriptivo (1 a 200 caracteres) y una `idempotency_key` única para el turno (reutilizar la misma clave únicamente si se reintenta el mismo envío).
5. Invocar la herramienta MCP `voice_submit_document(title, markdown, idempotency_key)`.
6. Entregar también la respuesta normal en el chat.

## Formato de redacción para voz (`markdown` enviado a Copilot)

- Redactar pensando en la escucha en voz alta: tono formal, claro, humano y conversacional en español.
- Se pueden usar encabezados simples (`#`, `##`) y párrafos breves para que la vista **Lectura** de Copilot separe visualmente cada bloque y permita pulsar «Leer desde aquí», pero cada párrafo debe sonar natural al hablarse de corrido.
- **No incluir en la redacción de voz:** bloques de código (` ``` `), comandos de terminal, rutas largas de archivos, nombres técnicos internos de herramientas ni URLs crudas.
- Empezar con una introducción breve de una o dos frases.
- Explicar en palabras simples lo esencial de lo realizado, el porqué y lo que sigue.
- Cerrar con una pregunta corta o una confirmación para el usuario.
- Ajustar la longitud a la complejidad del turno y mantener continuidad con los turnos anteriores del mismo chat.
