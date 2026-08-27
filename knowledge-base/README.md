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

La ingesta divide cada nota en chunks determinísticos de hasta 1800 caracteres,
conserva el título de la sección y agrega `section`/`chunk_index` a la metadata.
Al cambiar el esquema de chunks hay que volver a ejecutar la ingesta para que
Vectorize reciba la nueva representación; el primer chunk reutiliza el ID
histórico de cada documento para no dejar duplicados antiguos.
