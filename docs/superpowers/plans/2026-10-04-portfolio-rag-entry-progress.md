# Execution ledger — plan: 2026-10-04-portfolio-rag-entry.md

Pre-flight: el backend mantiene el contrato HTTP de fuentes; el frontend lo consume. Los metadatos nuevos de chunks son opcionales para compatibilidad con el índice actual.

Estado inicial: header ya actualizado; suite anterior de 67 pruebas y build aprobados. Hay cambios previos sin commit que se conservarán. Las operaciones sobre el índice remoto no forman parte de la implementación local.

Task 1: implementado. RED: seguimiento, filtrado y fallback en inglés fallaron; GREEN: 74 pruebas Python aprobadas. Contexto acotado de preguntas previas y página, score configurable, fuentes únicas, sección opcional y fallbacks localizados.
Task 2: implementado. RED: línea truncada y función de IDs retirados ausente; GREEN: 74 pruebas Python aprobadas, dry-run de 85 chunks sin credenciales/red. Evaluador offline y conjunto ampliado a 12 casos; no son mediciones de producción.
Task 3: helpers implementados. RED: módulos nuevos ausentes; GREEN: 7 tests Node. UI pendiente de QA visual/integración.
Task 4: parser/metadata/CV implementados. Regresión detectó YAML existente inválido (títulos con dos puntos sin comillas); se corrige el documento canónico conservando el título. Build pendiente tras esa corrección.

Task 3: QA fixture: un fallo 503 seguido de Reintentar conserva una pregunta visible; dos fuentes ES/EN de Eurosa se deduplican en un enlace interno; una fuente javascript se descarta. Límite de sesión ofrece Nueva charla, que limpia el error y habilita enviar.
Task 4: completo. Regresiones RED→GREEN de títulos YAML, CRLF y rol docente en Aquanova; Node 8/8, Astro 15 páginas. PDF copiado sin modificar.
Task 5: revisión independiente solicitada (read-only) sobre 41 archivos / 1683 líneas de diff contra snapshot previo; no incluye modificaciones ajenas anteriores en el vault. QA visual móvil y capturas en curso.

Final: revisión encontró tres Important, sin Critical ni Minor. Fix pass: seguimiento cuyo proyecto solo aparece en la respuesta (RED→GREEN), request_id estable con caché D1/claim para respuesta perdida (RED→GREEN), recuperación 429 con pregunta conservada/cooldown/reintento sin duplicación (RED→GREEN). Suite 78 Python y 9 Node aprobadas; ampliada regresión a replay al límite de sesión. Se agregó migración D1 0004, sin aplicarla remotamente.

Final: Ruling: mantener la evaluación remota y calibración fuera de esta implementación local, con umbral explícitamente provisional; costo si el valor inicial es inadecuado: consultas relevantes sin evidencia o recuperación insuficiente hasta calibrarlo.
Final: Ruling: la limpieza de vectores anteriores al primer manifest requiere inventario o reconstrucción al publicar; costo si se omite: fuentes retiradas todavía recuperables. Se documenta y no se modifica el índice remoto sin una operación de publicación.
Final: Ruling: conservar el CV existente, que marca 2023 frente al ≈2024 del perfil web; costo si no se reconcilia: inconsistencia visible para recruiters. PDF conservado byte por byte; hashes SHA256 coinciden.
Final: QA 320/768 dentro de marcos con anchos reales 305/753 tras scrollbar: contentWidth == clientWidth, sin desborde. Entrada con scripts bloqueados ofrece enlaces manuales y texto noscript. Menú móvil abre y cierra. Se usaron marcos por la aplicación asincrónica de la capacidad viewport en la pestaña de fondo; override restablecido.

Final: completo localmente. Verificación final leída: Python 79/79, Node 9/9, Astro 15 páginas, dry-run 85 chunks, git diff --check sin errores (solo avisos CRLF). Tres Important corregidos, ningún Minor diferido. Capturas inspeccionadas; revisión y notas preservadas porque no se realizaron commits. No se pide integración adicional: alcance local establecido; publicación requiere migración D1, API/web e índice.
