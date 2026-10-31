import type { DocumentDraft, DocumentOrigin } from '../../types/documents';

interface SampleDocument extends DocumentDraft {
  origin: DocumentOrigin;
  daysAgo: number;
}

/** Documentos de ejemplo que verá una cuenta nueva mientras no exista API 03. */
export const SAMPLE_DOCUMENTS: SampleDocument[] = [
  {
    // Mismo estilo que las redacciones de voz-skill: texto plano y conversacional.
    title: 'Redacción para voz: lo que hicimos hoy',
    format: 'text',
    origin: 'agent',
    daysAgo: 0,
    content: `Hoy dejamos lista la primera versión de la aplicación. Ya puedes entrar con tu cuenta y ver tus documentos en una biblioteca ordenada.

Lo más importante es que ahora puedes escuchar cualquier texto en el momento. La voz lee frase a frase, y en pantalla se ilumina lo que está diciendo, para que sigas la lectura con la vista.

Si te distraes, puedes pausar y continuar donde lo dejaste. También puedes saltar a la frase anterior o a la siguiente, o empezar desde cualquier párrafo.

¿Quieres que la próxima vez probemos otras voces?`,
  },
  {
    title: 'Bienvenida a Copilot',
    format: 'markdown',
    origin: 'web',
    daysAgo: 0,
    content: `# Bienvenida a Copilot

Copilot convierte tus documentos en una lectura en voz alta que puedes **pausar, continuar y reiniciar** cuando quieras.

## Cómo empezar

1. Crea un documento nuevo o importa un archivo \`.md\` o \`.txt\`.
2. Abre el documento y revisa la vista de **Lectura**.
3. Pulsa *Escuchar* y controla la reproducción desde la barra inferior.

> Consejo: la tecla Espacio pausa y continúa la lectura.

## Qué se lee y qué no

| Elemento | ¿Se lee? |
| --- | --- |
| Títulos y párrafos | Sí |
| Listas y citas | Sí |
| Bloques de código | No, se muestran en pantalla |

\`\`\`bash
pnpm dev
\`\`\`
`,
  },
  {
    title: 'Resumen de la reunión de producto',
    format: 'markdown',
    origin: 'agent',
    daysAgo: 0,
    content: `# Resumen de la reunión de producto

Enviado desde Codex al terminar la sesión.

## Decisiones

- La API se construye antes que la interfaz.
- Los documentos se guardan en un bucket privado.
- La voz se genera en el servidor y se reproduce en el navegador.

## Próximos pasos

1. Verificar sesiones de Clerk en FastAPI.
2. Guardar perfiles en Turso.
3. Evaluar voces en español.
`,
  },
  {
    title: 'Notas de lectura: arquitectura limpia',
    format: 'text',
    origin: 'web',
    daysAgo: 2,
    content: `Las dependencias del código fuente deben apuntar hacia dentro, hacia las políticas de más alto nivel.

Una capa externa conoce a la interna, nunca al revés. Así los detalles, como la base de datos o el framework, se pueden sustituir sin reescribir las reglas del negocio.

Pregunta para repasar: ¿qué parte de mi proyecto cambia más a menudo y dónde debería vivir?`,
  },
  {
    title: 'Revisión de código enviada por Claude Code',
    format: 'markdown',
    origin: 'agent',
    daysAgo: 3,
    content: `# Revisión del módulo de acceso

## Hallazgos

- El controlador descarta respuestas tardías con un contador de intentos.
- El cierre de sesión informa del fallo en lugar de suponer éxito.

## Sugerencia

Mantener la autorización en la API: el middleware de Nuxt solo decide la navegación.
`,
  },
  {
    title: 'Lista de vocabulario en inglés',
    format: 'text',
    origin: 'web',
    daysAgo: 6,
    content: `Throughput: cantidad de trabajo procesado por unidad de tiempo.

Latency: tiempo que tarda una petición en recibir respuesta.

Idempotent: una operación que produce el mismo resultado aunque se repita.`,
  },
];
