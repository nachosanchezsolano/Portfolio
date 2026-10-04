# Cambios del portfolio y chatbot

Implementación local de la auditoría `PORTFOLIO_RAG_AUDIT_2026-10-04.md` y la entrada solicitada.

## Entrada

`/` presenta a Nacho durante 1,2 segundos antes de abrir el idioma elegido: preferencia guardada, idiomas del navegador en orden, inglés por defecto. Español e English siempre son enlaces HTML normales. Dar foco o pasar el puntero sobre un enlace detiene la transición para permitir una elección manual. Las rutas `/es/` y `/en/` entran directamente. El movimiento reducido desactiva la animación; storage bloqueado no impide navegar ni usar el chat.

## Portfolio

Header literal: `AI Engenier- Nacho Sanchez`. Hero con foco AI Engineer y Full Stack, ejemplo concreto de la arquitectura del asistente, proyectos con rol/estado/fechas y enlaces de evidencia. Experiencia fechada, formación y CV general existente en `/resume/nacho-sanchez-ai-engineer.pdf` (español).

El CV existente indica inicio freelance en 2023; el perfil canónico dice aproximadamente 2024. Se conserva el PDF original y se usa la fecha aproximada del perfil en la web. No se agregaron métricas no respaldadas ni se publicó código de clientes o proyectos de estudiantes. Aquanova y Lessions identifican el rol docente/mentor.

## Chat y RAG

- El resolver recibe la pregunta actual junto con página y turnos recientes acotados (preguntas y respuestas) para resolver seguimientos; la pregunta actual controla cambios de tema. El historial se usa como referencia no confiable, nunca como evidencia nueva.
- Recuperación con `RAG_MIN_SCORE=0.7` configurable en Settings/Worker. Es un valor inicial **sin calibrar**, no una medición de calidad. El modelo de embeddings permanece `@cf/baai/bge-base-en-v1.5`; comparar un modelo multilingüe sigue requiriendo evaluación y nuevo índice.
- Se excluyen matches bajo el umbral/sin score, se deduplican chunks y fuentes y se conserva la sección opcional. Sin evidencia, el modelo se abstiene en el idioma de la interfaz.
- El navegador renderiza fuentes como enlaces internos permitidos, deduplicados por destino, sin confiar en URLs del modelo. Bienvenida, controles y fallbacks traducidos.
- Storage opcional, timeout de 15 segundos, errores de conexión/rate limit/validación/sesión. Reintentar conserva una sola pregunta visible. El límite de cinco preguntas ofrece nueva charla y nuevo ID de sesión.
- Cada pregunta lógica conserva `request_id` en sus reintentos. La API almacena la respuesta en D1 y evita consumir otro turno si se perdió la respuesta anterior. Una claim compartida entre Workers devuelve 409 mientras sigue procesando; su lease expira a los 120 segundos para permitir recuperar una ejecución interrumpida. Se requiere la migración `api/migrations/0004_chat_requests.sql` antes de desplegar la API.
- Ante 429 se restaura la pregunta editable y se ofrece reintento tras 60 segundos; ante 409, tras 5 segundos. Reenviar la misma pregunta pendiente conserva su ID y su burbuja. Una respuesta exitosa o nueva charla cierra ese estado pendiente.
- Ingestión: corregida pérdida de líneas al desbordar un chunk; source/sección forman parte del texto de embedding.

## Sincronización y evaluación

Desde la raíz del portfolio:

```powershell
python knowledge-base/scripts/upsert_vectorize.py --dry-run
python knowledge-base/scripts/upsert_vectorize.py --dry-run --prune
python knowledge-base/scripts/evaluate_retrieval.py --results resultados.json --k 4
```

Resultados offline: objeto JSON `{ "question-id": ["projects/source-es.md", ...] }`. El evaluador calcula Recall@K y MRR por fuentes únicas; la abstención mide resultados vacíos en los casos fuera del dominio. No mide faithfulness de generación. Los casos de seguimiento incluyen `retrieval_query` manual para evaluar recuperación independientemente del resolver.

`--remote` activa consultas explícitas al índice y embeddings facturables; no se ejecutó durante esta implementación. El dataset contiene doce casos ES/EN, seguimientos, cambio de tema, límites de evidencia y fuera del dominio. No se informa una precisión de producción sin ejecutar esa evaluación.

La ingestión real requiere credenciales y `--prune` para retirar IDs conocidos del manifest. El manifest conserva IDs pendientes si no se habilita prune y solo se actualiza tras solicitudes aceptadas por Cloudflare. Las mutaciones de Vectorize son asíncronas: comprobar su finalización antes de evaluar. Conservar el manifest local, usar uno por cuenta y no reutilizar un índice con otro modelo. La primera sincronización sin manifest no conoce vectores antiguos de documentos ya eliminados/privados: esa limpieza inicial requiere inventario remoto o reconstruir el índice. No se ejecutó reindexación ni eliminación remota.

## Verificación

Verificación final: **79 tests Python**, **9 tests Node**, build Astro de **15 páginas** y QA visual desktop/móvil. Los tests Python incluyen respuesta perdida y replay sin turno adicional, claves incompatibles y persistencia/claim D1 comprobadas con SQLite. Para el navegador se compiló una copia separada y se usó una API local simulada: prueba reintento sin duplicación, fuentes únicas/seguras, reinicio y recuperación 429; no certifica la calidad del modelo remoto. Los archivos finales de `apps/web/dist` usan la URL de API de producción.

La entrada sin JavaScript se comprobó dentro de un iframe sandbox sin permisos de scripts. Layouts de 320/768 px verificados en marcos: ancho de contenido igual al disponible, sin scroll horizontal. Capturas: `docs/audits/2026-10-04/portfolio-entry-desktop.png`, `portfolio-updated-desktop.png` y `portfolio-updated-mobile.png`.

El despliegue del sitio/API, sincronización del índice y calibración del umbral siguen pendientes de publicación. La API de producción estuvo bloqueada por el cliente durante la auditoría previa; no se afirma que esté caída ni que su respuesta real esté validada.

Orden de publicación: aplicar las migraciones D1 pendientes, desplegar API, publicar web; después sincronizar/evaluar el índice. El contrato `request_id` es opcional para clientes antiguos.

## Publicación autorizada el 2026-10-04

Se aplicaron en producción `0002_chat_trace.sql`, `0003_backfill_chat_trace.sql` y `0004_chat_requests.sql` con la sesión OAuth de Cloudflare. La consulta posterior confirmó cero migraciones pendientes y las tablas `chat_sessions`, `chat_messages` y `chat_requests`. El backfill conservó las 13 observaciones existentes y produjo 13 mensajes históricos.

Antes del commit se repitieron las 79 pruebas Python, las 9 pruebas Node, el build Astro de 15 páginas y `git diff --check`, todos correctos. El push a `main` activa el workflow existente de despliegue de API y frontend. La sincronización de Vectorize y la evaluación remota continúan pendientes.
