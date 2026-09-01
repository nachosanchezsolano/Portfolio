# Rediseño estratégico del portfolio

## Decisión central

El producto principal es el portfolio profesional de Jorge Ignacio Sánchez:

> I build full-stack products with AI.

La IA es una especialización dentro de Software Engineering. El chatbot es una
feature demostrativa y contextual, no la homepage ni el requisito para entender
el perfil.

## Audiencia y percepción objetivo

La audiencia primaria es recruiter o hiring manager técnico buscando perfiles
Junior+ / Semi-Senior para:

- AI Engineer
- Full-Stack AI Engineer
- Full-Stack Developer en productos con IA
- Software Engineer con foco en LLMs, RAG o integraciones AI
- Backend / Full-Stack Engineer en equipos de AI products

En 5 segundos debe entender: **Software Engineer orientado a Full-Stack + AI**.

En 20 segundos debe ver: **experiencia construyendo software real**.

En 60 segundos debe comprobar: **AI Engineering aplicado con arquitectura,
producción y trade-offs**.

## Arquitectura de información

### Navegación principal

Desktop:

`Nacho Sánchez` · `Work` · `Experience` · `About` · `Resume` · `Ask AI`

Mobile:

`Work` · `Experience` · `About` y `Ask AI` siempre accesible.

### Homepage

1. **Hero**
   - H1: `I build full-stack products with AI.`
   - Subheadline concreta sobre TypeScript, Python, aplicaciones de producción e
     integraciones con LLMs.
   - CTA primario: `View my work`.
   - CTA secundario: `Ask my AI assistant`.
   - Señales rápidas: TypeScript · Python · Next.js/Astro · AI/LLMs.
   - Ubicación y disponibilidad: Argentina · Open to remote opportunities.

2. **Proof bar**
   - Solo métricas comprobables.
   - Si no hay una métrica sólida, usar evidencia cualitativa: `Production
     software`, `Public deployments`, `Open-source system`.
   - No publicar números inventados ni claims imposibles de defender.

3. **Selected engineering work**
   - Exactamente tres proyectos principales.
   - Orden recomendado: AI Portfolio Assistant, proyecto full-stack en
     producción y proyecto backend/AI complementario.
   - Cada entrada muestra problema, rol, resultado, stack esencial y links.

4. **AI assistant invitation**
   - Mensaje: `Don't want to browse? Ask my AI assistant.`
   - Tres preguntas sugeridas.
   - El chatbot se abre bajo demanda y recibe contexto de la sección o proyecto.

5. **How I build software**
   - Product thinking.
   - Software Engineering.
   - Production.
   - AI Engineering.
   - Una frase por eje, sin convertirlo en un manifiesto largo.

6. **Experience**
   - Timeline o lista limpia.
   - Máximo 3–5 bullets por experiencia.
   - Priorizar responsabilidad, software real, impacto y producción.

7. **Skills**
   - Agrupadas por área, sin porcentajes, barras ni estrellas.
   - Frontend, Backend, AI Engineering, Data e Infrastructure.

8. **About**
   - Dos o tres párrafos sobre la combinación de Software Engineering + AI.

9. **Contact**
   - `Let's build something useful.`
   - LinkedIn, GitHub, email y resume.

## Wireframe de baja fidelidad

```text
┌──────────────────────────────────────────────────────────────┐
│ Nacho Sánchez       Work  Experience  About  Resume  Ask AI ✦ │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ I build full-stack products with AI.        [visual/evidence] │
│ Software Engineer focused on production-ready applications   │
│ using TypeScript, Python, LLMs and modern web technologies.  │
│                                                              │
│ [View my work]  [Ask my AI assistant ✦]                      │
│ TypeScript · Python · Next.js · AI/LLMs · Argentina           │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ Proof: [verifiable metric] [production] [deployment/evidence] │
├──────────────────────────────────────────────────────────────┤
│ SELECTED ENGINEERING WORK                                   │
│                                                              │
│ 01  AI Portfolio Assistant                                   │
│     Problem → decision → result                              │
│     RAG · Embeddings · LLM · Vector Search · Cloudflare      │
│     [Case study] [Live demo] [GitHub]                        │
│                                                              │
│ 02  Production Full-Stack Project                            │
│     Real users/devices · architecture · deployment           │
│     [Case study] [Live demo]                                 │
│                                                              │
│ 03  Backend / AI Engineering Project                         │
│     FastAPI · PostgreSQL · jobs · testing · observability    │
│     [Case study] [GitHub]                                    │
├──────────────────────────────────────────────────────────────┤
│ DON'T WANT TO BROWSE?                                       │
│ Ask my AI assistant about my work.               [Ask AI ✦] │
├──────────────────────────────────────────────────────────────┤
│ HOW I BUILD SOFTWARE                                        │
│ Product thinking | Software Engineering | Production | AI   │
├──────────────────────────────────────────────────────────────┤
│ EXPERIENCE                                                   │
├──────────────────────────────────────────────────────────────┤
│ SKILLS                                                       │
├──────────────────────────────────────────────────────────────┤
│ ABOUT                                                        │
├──────────────────────────────────────────────────────────────┤
│ LET'S BUILD SOMETHING USEFUL                                │
│ LinkedIn · GitHub · Email · Resume                           │
└──────────────────────────────────────────────────────────────┘
```

## Modelo de un engineering case study

Cada proyecto principal debe tener una página propia con esta secuencia:

1. Resumen de una frase y links.
2. Problem.
3. Context.
4. Constraints.
5. My role.
6. Architecture, idealmente con diagrama responsive.
7. Engineering decisions y alternativas consideradas.
8. Implementation.
9. Security.
10. AI pipeline, cuando corresponda.
11. Evaluation.
12. Deployment y observability.
13. Performance y cost, separando measured de estimated.
14. Challenges y what went wrong.
15. What I'd improve.
16. What I learned.

La regla editorial de cada sección es:

> Problem → Decision → Engineering → Result.

## Selección inicial de proyectos

### 01 — AI Portfolio Assistant

Debe demostrar RAG, embeddings, retrieval, citas, seguridad, observabilidad y
una experiencia AI útil.

### 02 — Production Full-Stack Project

Debe demostrar usuarios o dispositivos reales, CMS/API, caching, deployment,
restricciones, mantenimiento y evolución de producto.

### 03 — Backend / AI Engineering Project

Debe reforzar Python, FastAPI, PostgreSQL, background jobs, testing, Docker,
observability y una integración AI defendible.

Los proyectos restantes pasan a `Supporting work`, no compiten visualmente con
los tres principales.

## Reglas visuales

- Dirección: engineering + AI + minimal + premium + editorial.
- Mantener la paleta oscura existente solo si favorece legibilidad y contraste.
- Un acento dominante, sin neón excesivo ni gradientes violetas genéricos.
- Tipografía con personalidad, pero cuerpo legible y no menor a 16px en móvil.
- Motion sutil para jerarquía, feedback y transición; no para decorar.
- No usar cyberpunk, robots, cerebros, circuitos, galaxias ni terminales falsos.
- No esconder contenido detrás del chatbot.
- No usar porcentajes de skills ni diez cards equivalentes.

## Criterios de aceptación de Stage 1

- [x] El chatbot deja de ser la narrativa principal del rediseño.
- [x] La homepage tiene una jerarquía definida antes de tocar componentes.
- [x] El CTA primario es ver el trabajo; el chat es secundario.
- [x] Se definieron tres categorías de proyectos principales.
- [x] Existe un wireframe completo.
- [x] Existe una plantilla de case study.
- [ ] Se validaron roles objetivo, métricas disponibles y CTA final con el dueño
      del portfolio.

## Siguiente implementación

1. Rehacer `index.astro` alrededor de esta jerarquía.
2. Crear un componente reutilizable para proyecto destacado.
3. Añadir contenido real de los tres proyectos principales.
4. Extraer el chatbot a CTA secundario + botón flotante + sección contextual.
5. Crear la plantilla de case study del AI Portfolio Assistant.
