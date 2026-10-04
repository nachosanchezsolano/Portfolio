# Portfolio, RAG y pantalla de entrada — Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task, with TDD and a final independent review.

**Goal:** Aplicar la auditoría aprobada y mostrar una entrada accesible antes de resolver el idioma.

**Architecture:** Mantener Astro estático y las rutas `/es/` y `/en/`. Separar política de idioma, fuentes y errores en funciones pequeñas. Mantener los ports del backend y contextualizar la búsqueda antes de generar la respuesta. Gestionar ingestión y evaluación con herramientas explícitas, sin modificar el servicio remoto durante esta tarea.

**Tech Stack:** Astro, TypeScript, Node test runner, Python 3.13, pytest, Cloudflare Workers AI/Vectorize/D1.

**Spec:** `docs/PORTFOLIO_RAG_AUDIT_2026-10-04.md` y solicitud de pantalla inicial del usuario.

## Global Constraints

- Preservar los cambios previos y el header literal `AI Engenier- Nacho Sanchez`.
- Trabajar en este checkout: la implementación actual incluye archivos sin commit que otro worktree no tendría. No hacer commits, pushes, despliegues ni reindexaciones remotas.
- La pantalla inicial aparece en `/`; las rutas de idioma siguen entrando directamente. Preferencia guardada, luego idiomas del navegador, luego inglés. Siempre ofrecer enlaces manuales sin JavaScript.
- Mantener el modelo de embeddings actual. El umbral inicial de relevancia será configurable y se documentará como provisional, no calibrado.
- No inventar métricas, producción del chatbot comercial ni experiencia. Demos y repositorios solo desde `evidence`.
- Usar el CV general de AI Engineer existente, sin alterar el PDF ni publicar externamente.
- Los tests de Python no deben llamar servicios facturables. La evaluación remota será una opción explícita.

## Review Focus

- Storage bloqueado: el usuario debe poder entrar y escribir al chatbot.
- Preguntas de seguimiento y cambio de tema: recuperar el proyecto pertinente sin sustituir la pregunta actual.
- Error de API, timeout y límite de sesión: controles útiles, sin duplicar preguntas al reintentar.
- Documentos eliminados o privados: la planificación de sincronización debe detectar IDs retirados y conservar manifests únicamente de operaciones exitosas.
- Entrada sin JavaScript, movimiento reducido y pantallas a 320/768 px: acceso manual y layout sin desborde.

## Task 1: Backend contextual y recuperación de evidencia

**Files:** `api/src/application/use_cases/detect_intent.py`, `api/src/application/chat_controller.py`, `api/src/entities/chat.py`, `api/src/frameworks_and_drivers/cloudflare_ai.py`, `api/src/frameworks_and_drivers/settings.py`, `api/src/frameworks_and_drivers/cloudflare_worker_controller.py`; tests en `api/tests/test_rag_regressions.py`.

**Interfaces:** `DetectIntent.execute(message, conversation=None, page_context=None)` produce un `IntentDecision`. `CloudflareVectorizeRetriever(min_score=0.7)` devuelve chunks únicos pertinentes con metadata de sección. El contrato HTTP mantiene `sources: string[]`.

- [x] Escribir y ejecutar regresiones: consulta autónoma con historial/página; consulta simple conservada; match bajo excluido; fuentes únicas y fallback en inglés.
- [x] Implementar contextualización acotada, filtros de recuperación y fallbacks localizados.
- [x] Verificar los tests nuevos y la suite Python completa.

## Task 2: Ingestión sin pérdida y evaluación reproducible

**Files:** `knowledge-base/scripts/upsert_vectorize.py`, nuevo `knowledge-base/scripts/evaluate_retrieval.py`, `knowledge-base/evaluation/questions.json`, `api/tests/test_knowledge_base_chunking.py`, `api/tests/test_knowledge_base_evaluation.py`.

**Interfaces:** planificación de sincronización devuelve IDs retirados por índice/modelo. `--dry-run` no necesita credenciales; `--prune` habilita retirada explícita de IDs conocidos. La evaluación emite Recall@K/MRR y casos fallidos desde resultados recuperados, o consulta el índice remoto solo con una opción explícita.

- [x] Regresión RED: preservar líneas que cruzan el límite y detectar chunks retirados sin borrar otro índice.
- [x] Corregir chunking; conservar sección en los embeddings; agregar manifest y dry-run con prune explícito.
- [x] Agregar evaluación de resultados y dataset ES/EN/seguimientos/fuera del dominio con expectativas respaldadas.
- [x] Ejecutar pruebas y dry-run sin reindexar.

## Task 3: Entrada, chatbot y navegación bilingüe

**Files:** `apps/web/src/pages/index.astro`, `src/shared/i18n/localePreference.ts`, helpers de fuentes/errores del chat, `Chatbot.astro`, `chatService.ts`, `chatStore.ts`, locales y estilos; tests Node en `apps/web/tests`.

**Interfaces:** política pura de idioma devuelve `en | es`; preferencia se recuerda al usar el selector. Las fuentes se convierten únicamente en rutas internas permitidas. Errores tipados controlan reintento/reinicio.

- [x] Tests RED: idiomas ordenados, preferencia inválida/storage ausente, fuentes únicas seguras, límites/error/timeout y reinicio de store.
- [x] Implementar entrada breve con detección y enlaces manuales. Inicializar chat desde el copy de la página; traducir controles y fuentes.
- [x] Implementar reintentos sin duplicados, fin de sesión y reset. Corregir etiqueta accesible.
- [x] Ejecutar tests Node y verificar navegación/entrada en navegador.

## Task 4: Proyectos, experiencia y evidencia visual

**Files:** `src/shared/content/projects.ts`, `PortfolioHome.astro`, ruta de casos de estudio, CSS, `public/resume/nacho-sanchez-ai-engineer.pdf`.

**Interfaces:** `parseProjectSource` lee YAML estructurado, fecha, rol y `evidence`; `getProjects` mantiene rutas actuales. Las páginas usan fechas/estado orientados al lector y solo enlaces seguros.

- [x] Test RED: YAML anidado, cuerpo con separadores, fechas y enlaces ausentes/seguros.
- [x] Declarar parser YAML disponible como dependencia directa; completar enlaces, roles y fechas.
- [x] Sustituir gráfico orbital por evidencia del sistema; agregar cronología respaldada, acceso al CV y foco AI Engineer.
- [x] Ejecutar tests Node, build Astro, suite Python y QA visual desktop/móvil.

## Task 5: Revisión y entrega

- [x] Generar paquete de revisión con diferencias contra snapshot inicial, incluyendo archivos nuevos y evidencia de pruebas.
- [x] Revisión independiente conforme a executing-plans; corregir fallas materiales con regresiones.
- [x] Guardar capturas del resultado y actualizar documentación de configuración/limitaciones.
- [x] Entregar cambios locales verificados; señalar que despliegue y sincronización del índice quedan para publicación.
