# Knowledge base

Este directorio se puede abrir como vault en Obsidian. Solo agregar información que quieras hacer pública. No guardar CV privado, documentos de identidad ni claves. Los datos de contacto solo deben agregarse cuando exista autorización explícita para publicarlos.

`scripts/build_index.py` genera un índice local ignorado por Git.

Para cargar la base pública en Cloudflare Vectorize, usar el script de ingesta
con credenciales únicamente en variables de entorno:

```powershell
$env:CLOUDFLARE_ACCOUNT_ID = "<account-id>"
$env:CLOUDFLARE_API_TOKEN = "<token>"
uv run python knowledge-base/scripts/upsert_vectorize.py
```

El script filtra `visibility: public`, genera embeddings con
`@cf/baai/bge-base-en-v1.5` y sube metadata `source`/`content`, que es el
contrato consumido por el retriever de la API.
