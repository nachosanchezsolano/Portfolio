# Plan de finalización del portfolio

## Objetivo

Publicar un portfolio profesional bilingüe que comunique rápidamente el perfil,
muestre casos de estudio verificables y use el asistente conversacional como
una extensión útil del contenido, no como sustituto de la navegación.

## Prioridad de producto

El orden de trabajo está definido por impacto para una persona que llega al
portfolio —recruiter, hiring manager o colaborador técnico—:

1. Entender quién es Jorge y qué tipo de problemas resuelve.
2. Ver evidencia concreta en proyectos y trayectoria.
3. Contactarlo o visitar sus perfiles profesionales.
4. Explorar detalles mediante el chat con respuestas fundamentadas.

## Fases y entregables

### Fase 0 — Definición profesional

- [ ] Elegir 2–3 roles objetivo.
- [ ] Escribir una propuesta de valor de una frase en español e inglés.
- [ ] Seleccionar tres proyectos principales y uno secundario.
- [ ] Definir el CTA principal: contacto, LinkedIn o GitHub.
- [ ] Reemplazar placeholders de avatar y enlaces sociales.

**Terminado cuando:** una persona externa puede explicar en menos de 15 segundos
qué hace Jorge, para quién y con qué fortalezas.

### Fase 1 — Contenido y casos de estudio

- [ ] Crear una nota Markdown pública por proyecto.
- [ ] Documentar para cada proyecto: contexto, problema, responsabilidad,
  decisiones, stack, restricciones, resultado y aprendizajes.
- [ ] Agregar métricas o evidencia verificable cuando existan.
- [ ] Completar perfil, experiencia, estudios y habilidades.
- [ ] Revisar consistencia ES/EN y eliminar claims no respaldados.

**Terminado cuando:** cada proyecto principal tiene una historia completa y el
chat puede responder preguntas sobre él citando la fuente correspondiente.

### Fase 2 — Experiencia navegable

- [ ] Crear rutas o vistas indexables para proyectos, experiencia, estudios y
  sobre mí.
- [ ] Convertir las tarjetas-resumen actuales en entradas navegables.
- [ ] Añadir filtros o agrupación solo si ayudan a comparar proyectos.
- [ ] Mantener la navegación profunda enlazable y compatible con el botón atrás.
- [ ] Implementar el selector ES/EN de extremo a extremo.

**Terminado cuando:** cada sección tiene contenido real, URL o estado profundo,
traducción completa y navegación usable sin depender del chat.

### Fase 3 — Dirección visual y UX

Aplicar `frontend-design`, `design-taste-frontend` y `ui-ux-pro-max`.

- [ ] Fijar una dirección visual: portfolio de desarrollador, dark-tech
  editorial, con variación controlada y densidad media.
- [ ] Mantener un solo sistema de tokens y una sola familia visual de iconos.
- [ ] Revisar jerarquía del hero, CTA, proyectos y evidencia.
- [ ] Reemplazar textos placeholder y símbolos decorativos por contenido o
  iconos semánticos.
- [ ] Completar estados loading, vacío, error, offline y retry.
- [ ] Verificar teclado, focus visible, lectores de pantalla y targets táctiles.
- [ ] Probar móvil pequeño, móvil grande, tablet y escritorio.
- [ ] Mantener `prefers-reduced-motion` y evitar animaciones decorativas sin
  propósito.

**Terminado cuando:** una revisión visual y funcional no encuentra bloqueos de
accesibilidad, navegación, responsive ni estados incompletos.

### Fase 4 — SEO y performance

Aplicar `seo-audit` y `web-design-guidelines`.

- [ ] Definir títulos y descripciones únicas por ruta y por idioma.
- [ ] Agregar canonical, hreflang y `x-default` coherentes.
- [ ] Crear `robots.txt` y sitemap con URLs indexables.
- [ ] Agregar JSON-LD de `Person`, `WebSite` y proyectos relevantes.
- [ ] Añadir Open Graph y Twitter/X cards.
- [ ] Servir fuentes con `@font-face`, `font-display: swap` y variantes mínimas.
- [ ] Optimizar imágenes a AVIF/WebP con dimensiones declaradas.
- [ ] Medir y corregir LCP, INP y CLS.

**Terminado cuando:** las rutas públicas son indexables, las dos variantes de
idioma están correctamente relacionadas y la auditoría móvil no detecta
problemas críticos.

### Fase 5 — Chat basado en evidencia

Aplicar `senior-prompt-engineer`, `evaluate-rag` y `rag-architect`.

- [ ] Crear un golden set de preguntas en español e inglés.
- [ ] Cubrir proyectos, experiencia, habilidades, decisiones y preguntas sin
  evidencia.
- [ ] Medir Precision@K, Recall@K, MRR/NDCG, faithfulness y relevancia.
- [ ] Revisar chunking y metadata de las notas públicas.
- [ ] Mostrar fuentes como elementos inspeccionables dentro de la UI.
- [ ] Definir umbral de confianza y respuesta segura cuando no haya evidencia.
- [ ] Probar prompt injection, PII, contenido privado y preguntas ambiguas.
- [ ] Registrar latencia, `context_count`, errores y uso sin guardar PII.

**Terminado cuando:** el dataset pasa umbrales definidos, las respuestas
incluyen citas útiles y las preguntas fuera de alcance no generan invenciones.

### Fase 6 — Release

- [ ] Ejecutar tests de API y frontend.
- [ ] Verificar build de Astro y deploy de API.
- [ ] Validar el dominio público desde móvil y escritorio.
- [ ] Revisar variables públicas y confirmar que no hay secretos en el bundle.
- [ ] Actualizar README, documentación de desarrollo y guía de contenido.
- [ ] Crear changelog y elegir licencia antes del release público.

**Terminado cuando:** el repositorio se puede ejecutar siguiendo el README, el
portfolio publicado funciona en ES/EN y existe una checklist de rollback.

## Orden recomendado de implementación

1. Fase 0 y Fase 1: propuesta de valor y contenido real.
2. Fase 2: rutas, casos de estudio y selector de idioma.
3. Fase 3: refinamiento visual y accesibilidad.
4. Fase 4: SEO y performance.
5. Fase 5: evaluación y endurecimiento del chatbot.
6. Fase 6: release.

## Primer sprint concreto

1. Definir roles objetivo y CTA.
2. Escribir el caso de estudio del asistente del portfolio.
3. Escribir dos casos de estudio adicionales.
4. Implementar una ruta de proyecto reutilizable desde Markdown.
5. Hacer funcional ES/EN.
6. Añadir fuentes visibles a las respuestas del chat.
7. Ejecutar una auditoría responsive y de accesibilidad.

## Criterio de éxito de la primera versión

Una visita nueva debe poder entender el perfil, abrir tres proyectos, cambiar de
idioma, llegar a un enlace de contacto y hacer una pregunta al asistente en
menos de dos minutos, sin encontrar placeholders ni respuestas sin evidencia.
