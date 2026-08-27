# Tests

Tests are organized by purpose: unit, integration, contract, evaluation, and end-to-end.

## Política de consumo de tokens

La suite normal debe ser completamente offline y no puede llamar a Workers AI,
Vectorize ni a ningún proveedor remoto facturable:

```powershell
cd "C:\Users\nacho\OneDrive\Documents\Job applying System\portfolio-platform\api"
uv run pytest -q -m "not token"
```

Todo test que consuma tokens debe vivir en `api/tests/token/` y estar marcado con
`@pytest.mark.token`. Esos tests no se ejecutan en cada push ni antes de que se
modifiquen sus propios archivos. Se ejecutan explícitamente con:

```powershell
uv run pytest -q -m token
```

Los tests que validan modelos y prompts deben usar dobles locales, como
`test_cloudflare_adapters.py`; por eso pueden ejecutarse siempre sin costo.
