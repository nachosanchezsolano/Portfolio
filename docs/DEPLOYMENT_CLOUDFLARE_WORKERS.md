# Guía de deploy de la API en Cloudflare Workers

Esta guía despliega la API FastAPI como un Python Worker usando:

```text
FastAPI + ASGI
        ↓
Cloudflare Worker
        ├── Workers AI: intención y respuesta
        └── Vectorize: recuperación semántica
```

Cloudflare soporta FastAPI mediante ASGI. Python Workers sigue en open beta y
ejecuta Python sobre Pyodide, por lo que conviene validar las dependencias antes
de usarlo como único runtime de producción.

Documentación oficial:

- [FastAPI en Python Workers](https://developers.cloudflare.com/workers/languages/python/packages/fastapi/)
- [Python Workers](https://developers.cloudflare.com/workers/languages/python/)
- [Paquetes Python soportados](https://developers.cloudflare.com/workers/languages/python/packages/)
- [Configuración de Wrangler](https://developers.cloudflare.com/workers/wrangler/configuration/)

## 1. Requisitos

Instalar Node.js y uv. También se necesita una cuenta Cloudflare con Workers AI
habilitado y permisos para Workers, Workers AI y Vectorize.

Desde PowerShell:

```powershell
cd "C:\Users\nacho\OneDrive\Documents\Job applying System\portfolio-platform\api"
uv sync --group dev
uv run pytest -q -m "not token"
```

La suite offline debe terminar con 62 passed y no consumir tokens.

## 2. Autenticar Wrangler

```powershell
npx wrangler@latest login
npx wrangler@latest whoami
```

No guardar tokens en el repositorio. En CI/CD deben configurarse como secretos.

## 3. Crear Vectorize

La API usa @cf/baai/bge-base-en-v1.5, que produce vectores de 768 dimensiones.
Crear el índice con exactamente esa dimensión:

```powershell
npx wrangler@latest vectorize create portfolio-knowledge --dimensions=768 --metric=cosine
```

El índice debe coincidir con api/wrangler.jsonc:

```json
{
  "binding": "VECTORIZE",
  "index_name": "portfolio-knowledge"
}
```

La dimensión y la métrica son fijas después de crear el índice.

Documentación oficial:

- [Crear índices Vectorize](https://developers.cloudflare.com/vectorize/best-practices/create-indexes/)
- [Vectorize con embeddings de Workers AI](https://developers.cloudflare.com/vectorize/get-started/embeddings/)
- [Consultar vectores](https://developers.cloudflare.com/vectorize/best-practices/query-vectors/)

## 4. Cargar documentos

Crear el índice no carga documentos. Cada vector debe incluir metadata:

```json
{
  "source": "profile/principles.md",
  "content": "Me interesa crear soluciones simples, seguras y fáciles de evolucionar."
}
```

El retriever utiliza source como cita, content como contexto y section/chunk_index
para identificar cada fragmento. Las notas públicas se dividen por secciones y
tamaño antes de generar embeddings. Después de modificar la base de conocimiento
hay que volver a ejecutar:

```powershell
uv run python knowledge-base/scripts/upsert_vectorize.py
```

Sin vectores cargados, la API desplegará correctamente pero devolverá el fallback
de evidencia insuficiente.

## 5. Revisar configuración

La configuración actual está en api/wrangler.jsonc.

Debe contener:

```json
{
  "name": "portfolio-api",
  "main": "src/worker.py",
  "compatibility_flags": ["python_workers"],
  "ai": {
    "binding": "AI",
    "remote": true
  },
  "vectorize": [
    {
      "binding": "VECTORIZE",
      "index_name": "portfolio-knowledge",
      "remote": true
    }
  ]
}
```

Configurar el origen real del frontend:

```json
"vars": {
  "APP_ENV": "production",
  "ALLOWED_ORIGINS": "https://portfolio.example.com",
  "RATE_LIMIT_REQUESTS": "30",
  "RATE_LIMIT_WINDOW_SECONDS": "60"
}
```

No guardar secretos dentro de vars.

## 6. API key

La API key es opcional. El frontend actual llama directamente desde el navegador
y no debe recibir una API key secreta. Para el portfolio público inicial usar
CORS estricto y protección distribuida de Cloudflare. Crear `API_KEY` solo para
consumidores server-to-server o detrás de un proxy propio:

```powershell
npx wrangler@latest secret put API_KEY
```

Wrangler solicitará el valor de forma interactiva. Los secretos no deben estar
en wrangler.jsonc, .env versionado ni en el frontend.

Documentación: [Secrets de Workers](https://developers.cloudflare.com/workers/configuration/secrets/).

## 7. Probar localmente

Desde api:

```powershell
uv run pywrangler dev
```

Para probar bindings reales de Workers AI y Vectorize, usar el modo remoto:

```powershell
uv run pywrangler dev --remote
```

Smoke test:

```powershell
$body = @{
  message = "¿Qué arquitectura técnica estás construyendo?"
  session_id = "local-smoke-test"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://localhost:8787/v1/chat `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

El Docker Compose continúa disponible para el modo local tradicional:

```powershell
cd "C:\Users\nacho\OneDrive\Documents\Job applying System\portfolio-platform"
docker compose -f docker-compose.dev.yml up --build
```

## 8. Deploy

Desde api:

```powershell
uv run pywrangler deploy
```

Pywrangler empaqueta las dependencias declaradas en pyproject.toml y Wrangler
publica el Worker. [Deploy de Python Workers](https://developers.cloudflare.com/workers/languages/python/).

La salida mostrará una URL similar a:

```text
https://portfolio-api.<subdominio>.workers.dev
```

## 9. Verificar producción

```powershell
$apiUrl = "https://portfolio-api.<subdominio>.workers.dev"
Invoke-RestMethod "$apiUrl/health"

$body = @{
  message = "¿Qué arquitectura técnica estás construyendo?"
  session_id = "production-smoke-test"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "$apiUrl/v1/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Validar también 401 con una API key incorrecta, 400 con SQL o prompt injection,
422 con un request inválido, 429 al superar el rate limit y respuestas con sources.

## 10. Dominio personalizado

Desde Cloudflare Dashboard:

```text
Workers & Pages
  → portfolio-api
  → Settings
  → Domains & Routes
  → Add Custom Domain
```

También puede declararse en Wrangler:

```json
"routes": [
  {
    "pattern": "api.example.com",
    "custom_domain": true
  }
]
```

Documentación: [Custom Domains](https://developers.cloudflare.com/workers/configuration/routing/custom-domains/).

Después, configurar en el frontend:

```text
PUBLIC_API_URL=https://api.example.com
```

## 11. Seguridad y limitaciones actuales

La API ya valida inputs/outputs, sanitiza sintaxis y semántica, aplica CORS y
headers de seguridad. La API key solo aplica si se configura para un consumidor
server-to-server.

CloudflareRequestSecurity utiliza actualmente un rate limit en memoria. No es
distribuido entre isolates. Para producción, reemplazarlo por Cloudflare Rate
Limiting, Durable Objects o almacenamiento distribuido.

InMemorySessionRepository tampoco persiste entre evictions o despliegues. Antes
de usar sesiones persistentes, migrarlo a Durable Objects o D1.

Documentación: [SQLite Storage API de Durable Objects](https://developers.cloudflare.com/durable-objects/api/sqlite-storage-api/).

## Checklist

```text
[ ] uv sync --group dev
[ ] uv run pytest -q -m "not token"
[ ] Wrangler autenticado
[ ] Vectorize portfolio-knowledge creado
[ ] Vectores y metadata cargados
[ ] ALLOWED_ORIGINS configurado
[ ] API_KEY creado como secret si existe un consumidor server-to-server
[ ] pywrangler dev --remote validado
[ ] pywrangler deploy ejecutado
[ ] /health responde 200
[ ] /v1/chat devuelve sources
[ ] Frontend apunta a PUBLIC_API_URL
[ ] Custom Domain configurado
[ ] Rate limiting distribuido revisado
[ ] Persistencia de sesiones planificada
```
