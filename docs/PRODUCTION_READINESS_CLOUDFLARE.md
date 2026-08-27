# Readiness y guía final de producción

## Diagnóstico actual

La API está preparada para desplegarse como Python Worker. La arquitectura, los
adaptadores Cloudflare, la validación, la sanitización, el flujo de intención/RAG/
respuesta y el contrato HTTP están implementados.

La suite local offline está validada: `50 passed`.

| Área | Estado | Acción pendiente |
| --- | --- | --- |
| Código, arquitectura y tests | Listo | Ninguna acción manual |
| Wrangler y bindings | Configurado | Autenticar la cuenta |
| Workers AI | Configurado | Validar acceso en la cuenta |
| Vectorize | Pendiente | Crear índice y cargar documentos |
| API key | Pendiente | Crear secret |
| CORS | Pendiente | Reemplazar dominio de ejemplo |
| GitHub Actions | Listo | Agregar dos secrets |
| Frontend | Pendiente | Configurar `PUBLIC_API_URL` |
| Sesiones y rate limit | Demo | Migrar a componentes distribuidos |

La API puede publicarse como primera versión de bajo tráfico. Para una
producción robusta todavía deben resolverse las sesiones y el rate limit en
memoria, porque los isolates pueden reiniciarse y no comparten estado.

## 1. Validar localmente

Desde PowerShell:

```powershell
cd "C:\Users\nacho\OneDrive\Documents\Job applying System\portfolio-platform\api"
uv sync --group dev
uv run pytest -q -m "not token"
```

Resultado esperado: `50 passed`, sin consumir tokens.

## 2. Autenticar Cloudflare

Crear en Cloudflare un API Token con permisos mínimos para desplegar Workers y
obtener el Account ID. No guardar el token en Git, `.env`, `wrangler.jsonc` ni
el frontend.

```powershell
npx wrangler@latest login
npx wrangler@latest whoami
```

## 3. Crear Vectorize

El modelo `@cf/baai/bge-base-en-v1.5` requiere un índice de 768 dimensiones:

```powershell
npx wrangler@latest vectorize create portfolio-knowledge --dimensions=768 --metric=cosine
```

Debe coincidir con `api/wrangler.jsonc`:

```json
{
  "binding": "VECTORIZE",
  "index_name": "portfolio-knowledge",
  "remote": true
}
```

## 4. Cargar los documentos

La base contiene 14 documentos públicos bilingües en:

```text
knowledge-base/vault/
```

El script `knowledge-base/scripts/build_index.py` genera un índice JSON local,
pero todavía no sube embeddings a Vectorize. Antes del primer deploy funcional
hay que ejecutar un proceso de ingesta que:

1. Lea cada Markdown público.
2. Genere embeddings con Workers AI.
3. Inserte cada vector en `portfolio-knowledge`.
4. Guarde metadata `source` y `content`.
5. Excluya documentos privados, CVs y secretos.

Metadata mínima:

```json
{
  "source": "projects/grupo-eurosa-es.md",
  "content": "Contenido público del documento..."
}
```

Sin esta carga el Worker puede desplegarse, pero el RAG no tendrá evidencia y
devolverá contexto insuficiente.

## 5. Configurar CORS y decidir autenticación

En `api/wrangler.jsonc`, reemplazar el dominio de ejemplo:

```json
"ALLOWED_ORIGINS": "https://portfolio.example.com"
```

por el dominio real del frontend. No usar `*` en producción.

El frontend actual llama directamente al Worker desde el navegador y no envía
`X-API-Key`. Por eso no se debe poner una API key secreta en una variable
`PUBLIC_` ni dentro del bundle del frontend.

Para el portfolio público inicial hay dos opciones:

1. Dejar `API_KEY` vacío y proteger el endpoint con CORS estricto, rate limiting
   de Cloudflare y límites de la aplicación.
2. Crear un proxy server-side que mantenga la API key fuera del navegador.

Si se utiliza un consumidor server-to-server, crear el secret:

```powershell
npx wrangler@latest secret put API_KEY
```

Ese consumidor debe enviar `X-API-Key`. El frontend público no debe recibir ni
conocer ese valor.

## 6. Probar bindings remotos

```powershell
cd "C:\Users\nacho\OneDrive\Documents\Job applying System\portfolio-platform\api"
uv run pywrangler dev --remote
```

```powershell
Invoke-RestMethod http://localhost:8787/health

$body = @{
  message = "¿Qué proyectos desarrollaste?"
  session_id = "remote-smoke-test"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://localhost:8787/v1/chat `
  -Method Post `
  -Headers @{ "X-API-Key" = "<valor-configurado>" } `
  -ContentType "application/json" `
  -Body $body
```

## 7. Configurar GitHub Actions

En **GitHub → Settings → Secrets and variables → Actions**, crear:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

El workflow está en `.github/workflows/deploy-api-cloudflare.yml`. Los pull
requests ejecutan tests; un push a `main` que modifique `api/` ejecuta tests y
después el deploy.

## 8. Deploy

Manual:

```powershell
cd "C:\Users\nacho\OneDrive\Documents\Job applying System\portfolio-platform\api"
uv run pywrangler deploy
```

La URL será similar a:

```text
https://portfolio-api.<subdominio>.workers.dev
```

Frontend:

```text
PUBLIC_API_URL=https://portfolio-api.<subdominio>.workers.dev
```

## 9. Verificación de producción

Comprobar:

- `/health` responde `200`.
- `/v1/chat` responde con `message`, `intent`, `session_id` y `sources`.
- API key incorrecta devuelve `401`.
- SQL o prompt injection devuelve `400`.
- Request inválido devuelve `422`.
- El límite devuelve `429`.
- CORS permite solo el frontend real.
- Hay respuestas correctas en español e inglés.
- `sources` contiene documentos de Vectorize.

## 10. Pendientes para producción robusta

- Migrar `InMemorySessionRepository` a Durable Objects o D1.
- Reemplazar `CloudflareRequestSecurity` en memoria por Rate Limiting API o un
  mecanismo distribuido.
- Configurar dominio personalizado, por ejemplo `api.tudominio.com`.
- Revisar logs para evitar email, teléfono, API keys y PII.
- Configurar alertas de errores y consumo de Workers AI.
- Validar que solo documentos `visibility: public` lleguen a Vectorize.
- Rotar periódicamente la API key.

## Checklist

```text
[ ] Tests offline: 50 passed
[ ] Cloudflare autenticado
[ ] API token protegido
[ ] Vectorize creado con 768 dimensiones
[ ] 14 documentos bilingües indexados
[ ] Metadata source/content validada
[ ] ALLOWED_ORIGINS configurado
[ ] API_KEY creado como secret
[ ] pywrangler dev --remote validado
[ ] Secrets de GitHub configurados
[ ] Deploy ejecutado
[ ] /health responde 200
[ ] /v1/chat devuelve sources
[ ] PUBLIC_API_URL configurado
[ ] Dominio personalizado configurado
[ ] Sesiones distribuidas resueltas
[ ] Rate limiting distribuido resuelto
```

## Referencias oficiales

- [Python Workers y pywrangler](https://developers.cloudflare.com/workers/languages/python/packages/)
- [GitHub Actions para Workers](https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/)
- [Secrets de Workers](https://developers.cloudflare.com/workers/configuration/secrets/)
- [Insertar vectores en Vectorize](https://developers.cloudflare.com/vectorize/best-practices/insert-vectors/)
- [Consultar vectores en Vectorize](https://developers.cloudflare.com/vectorize/best-practices/query-vectors/)
- [Rate Limiting API](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/)
