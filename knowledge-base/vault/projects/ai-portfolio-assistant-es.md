---
id: project-ai-portfolio-assistant-es
type: project
title: Asistente AI del portfolio
visibility: public
status: published
technologies:
  - Astro
  - Python
  - FastAPI
  - Cloudflare Workers AI
  - Vectorize
  - Markdown
  - TypeScript
skills:
  - Desarrollo Full Stack
  - AI Engineering
  - RAG
  - Diseño de APIs
  - Seguridad
  - Observabilidad
evidence:
  github: https://github.com/nachosanchezsolano/Portfolio
  demo: https://nachosanchez.com.ar
---

# Resumen

Un portfolio conversacional basado en evidencia que permite explorar el trabajo profesional mediante páginas normales o preguntas en lenguaje natural.

# Problema

La información profesional suele estar distribuida entre CVs, descripciones de proyectos, notas y perfiles. Un portfolio estático puede mostrar trabajos, pero explica peor las decisiones y el contexto detrás de ellos.

# Contexto

Este proyecto es a la vez un portfolio profesional y una demostración pública de ingeniería de productos AI full stack. La misma fuente de conocimiento en Markdown alimenta el contenido del portfolio y el contexto de recuperación del asistente.

# Mi rol

Diseñé e implementé la dirección del producto, el frontend en Astro, el flujo de la aplicación FastAPI, el modelo de conocimiento, los adaptadores de Cloudflare, los controles de seguridad, los eventos de observabilidad y la documentación de despliegue.

# Arquitectura

El flujo desplegado es:

Navegador → assets estáticos de Astro → Worker FastAPI → detección de intención → recuperación en Vectorize → respuesta fundamentada → respuesta con fuentes.

La fuente canónica es Markdown bilingüe con frontmatter YAML. Los documentos públicos se dividen de forma determinística antes de generar embeddings y subir metadata al índice `portfolio-knowledge` de Vectorize.

# Decisiones de ingeniería

## Markdown como fuente de verdad

Markdown mantiene el contenido portable, revisable e independiente del editor. La misma información puede alimentar páginas, búsqueda y chat sin duplicar claims en diferentes lugares.

## Recuperación antes que generación sin respaldo

El asistente recupera evidencia pública antes de generar una respuesta. Cuando el contexto no es suficiente, responde de forma segura en lugar de presentar una afirmación no verificada como un hecho.

## Límites entre proveedores

Los proveedores de AI e infraestructura están detrás de ports y adapters de aplicación. Esto mantiene testeables los casos de uso y evita acoplar el dominio a una única implementación.

## Cloudflare para el producto público

El despliegue actual usa Cloudflare Workers, Workers AI y Vectorize para acercar el portfolio a sus visitantes y evitar exponer credenciales de API en el navegador.

# Pipeline AI

Documentos → filtro de visibilidad pública → chunking semántico por sección → embeddings → Vectorize → contexto recuperado → prompt de respuesta → respuesta fundamentada con fuentes.

El contrato actual de Vectorize usa 768 dimensiones, similitud coseno y metadata para source, content, section y chunk index.

# Seguridad y confiabilidad

- CORS permite únicamente los dominios configurados del portfolio.
- Las solicitudes pasan validación y sanitización sintáctica y semántica.
- Rate limiting y estado de sesión se controlan en la API.
- El navegador nunca recibe la API key.
- Los logs excluyen prompts, respuestas completas, secretos, IPs y PII automática.
- Los tests cubren prompt injection, exposición de contenido privado y respuestas sin evidencia.

# Estado de evaluación

El repositorio incluye tests offline de la API y una base de evaluación de la knowledge base. El próximo hito es ampliar el golden set para medir precisión de retrieval, faithfulness, latencia y costo. No se publica un porcentaje de exactitud de producción hasta completar ese dataset.

# Qué mejoraría

- Agregar un handoff contextual desde cada case study al asistente.
- Completar la estructura de rutas bilingües y su metadata recíproca.
- Añadir gates de regresión de retrieval y groundedness en CI.
- Incorporar sesiones y rate limiting distribuidos si el tráfico público lo requiere.

# Qué aprendí

Una feature AI es más confiable cuando se trata como una superficie normal de producto: límites claros de fuentes, estados de error explícitos, comportamiento observable y un fallback útil sin AI.
