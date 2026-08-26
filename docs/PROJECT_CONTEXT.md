# Project context

Este documento es el punto de entrada para cualquier nueva sesión de trabajo.
Describe el estado real del repositorio y tiene prioridad sobre documentos que
describen una arquitectura futura o histórica.

## Identidad del proyecto

- Repositorio: `nachosanchezsolano/Portfolio`
- Rama de producción: `main`
- Objetivo: portfolio profesional bilingüe con un chat basado en evidencia.
- Idiomas del portfolio y de la base de conocimiento: español e inglés.

## Arquitectura actual desplegada

```text
https://nachosanchez.com.ar
        │
        ▼
Worker portfolio-web
Astro static assets
        │
        ▼
https://porfolio-api.nachosanchez.com.ar
        │
        ▼
Worker portfolio-api
FastAPI + ASGI
        ├── Workers AI: intención y respuesta
        └── Vectorize: portfolio-knowledge
```

El frontend se compila y despliega desde GitHub Actions. Su directorio raíz es
`apps/web` y sus assets generados están en `apps/web/dist`, definidos en
`apps/web/wrangler.jsonc`.

La API se despliega desde `api` mediante `uv run pywrangler deploy`. Su entrada
es `api/src/worker.py` y usa `api/wrangler.jsonc`.

## Flujo de una consulta

```text
POST /v1/chat
  → CORS y headers de seguridad
  → RequestSecurity y rate limit
  → validación Pydantic
  → sanitización sintáctica
  → sanitización semántica
  → detección de intención con Workers AI
  → embedding y consulta Vectorize
  → respuesta grounded con Workers AI
  → ChatOutput con sources
```

El flujo de aplicación está en `api/src/application/chat_controller.py`.
Los proveedores concretos están en
`api/src/frameworks_and_drivers/providers/cloudflare/`.

## Estado funcional conocido

- La API responde `GET /health` con `200`.
- El preflight CORS para `https://nachosanchez.com.ar` responde `200`.
- Los tests de la API pasan localmente: `50 passed`.
- CORS configurado para:
  - `https://nachosanchez.com.ar`
  - `https://www.nachosanchez.com.ar`
- El navegador no debe recibir ni enviar `API_KEY`; la API es pública para el
  portfolio y se protege con CORS, límites y controles de Cloudflare.
- Las sesiones y el rate limit actuales son en memoria y no son distribuidos.
- Si la API devuelve `Todavía no tengo evidencia suficiente...`, revisar los
  logs `rag_completed` y el campo `context_count`. Un valor `0` indica que no
  se recuperaron chunks utilizables de Vectorize.

## Knowledge base

La fuente canónica está en `knowledge-base/vault/`. Solo se publica contenido
con `visibility: public`. Hay documentos bilingües de perfil y proyectos.

Vectorize debe usar:

```text
index: portfolio-knowledge
dimensions: 768
metric: cosine
metadata mínima: source, content
```

Crear el índice no carga documentos. La ingesta de embeddings y metadata es un
requisito independiente para que el chat pueda responder con evidencia.

## Observabilidad

La API emite logs JSON sin prompts, respuestas completas, secretos ni PII.
Eventos principales:

```text
request_started
message_sanitized
intent_detected
rag_completed
response_generated
chat_flow_completed
http_request_completed
```

Se consultan en Cloudflare: `Workers & Pages → portfolio-api → Observability → Logs`.

## Archivos que debe leer un chat nuevo

Orden recomendado:

1. Este documento.
2. `README.md` para el objetivo general.
3. `docs/API_FLOW.md` para el flujo de la API.
4. `SECURITY.md` para límites y reglas de seguridad.
5. `docs/CONTENT_SCHEMA.md` para agregar contenido.
6. `docs/DEPLOYMENT_CLOUDFLARE_WORKERS.md` para deploy manual de la API.
7. `.github/workflows/deploy-api-cloudflare.yml` para el deploy automatizado.

Leer `ARCHITECTURE.md`, los ADR y `apps/web/ARCHITECTURE.md` solo cuando la
tarea requiera entender decisiones de diseño más amplias.

## Documentación secundaria o histórica

- `docs/DEPLOYMENT_CLOUDFLARE_GITHUB.md`: alternativa legacy; no representa el
  deploy actual de Workers AI y Vectorize.
- `docs/PRODUCTION_READINESS_CLOUDFLARE.md`: checklist histórica; sus números,
  dominios y estados pueden estar desactualizados.
- `docs/DEVELOPMENT.md`, `docs/PRODUCT.md`, `docs/ROADMAP.md` y los ADR:
  describen objetivos o decisiones del engine futuro, no necesariamente el
  runtime actualmente desplegado.

## Reglas para continuar el trabajo

- No subir `.env`, `.dev.vars`, `.wrangler`, tokens, claves ni documentos
  privados.
- No cambiar el proveedor de IA sin pasar por los ports de aplicación.
- No poner secretos en variables `PUBLIC_` ni en el bundle del frontend.
- Mantener las respuestas limitadas a evidencia recuperada.
- Agregar o actualizar tests cuando cambie un contrato o una regla de negocio.
- Antes de afirmar que un problema está resuelto, revisar tests, workflow y
  comportamiento real del endpoint publicado.
