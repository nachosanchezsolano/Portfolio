# Chatbot experimental — conservación y reintegración

## Estado de esta adaptación (20 de octubre de 2026)

- Rama local de preservación: `codex/experimental-ai-chatbot`, commit `b3dfcf1`.
- Rama del portfolio: `codex/portfolio-profesional`.
- La rama experimental conserva el último código registrado del asistente antes de esta adaptación. Su funcionamiento con servicios remotos no se volvió a probar y depende de la configuración de Cloudflare.
- Los dos perfiles Markdown que ya tenían cambios sin commit permanecen en el checkout. No forman parte de ese checkpoint y no fueron sobrescritos ni incorporados a un commit.
- La adaptación inicial no realizó push, merge, despliegue ni modificación de secretos. Posteriormente el usuario autorizó el commit y push de la rama del portfolio; la rama experimental sigue siendo un respaldo local. No se autorizaron merge ni despliegue.

## Qué se conserva y qué se desconecta

`apps/web/src/features/home/components/Chatbot.astro`, `services/`, `stores/`, entidades, traducciones y tests del chat se conservan. Los imports y montajes de portada y casos de estudio están comentados. La rama experimental conserva también sus antiguos textos, sugerencias y configuración de cada página.

La web pública usa `professional-portfolio.css`; los estilos anteriores del asistente permanecen en sus archivos sin cargarse desde las páginas nuevas. Ningún bundle público debe incluir su transporte de red.

El Markdown `knowledge-base/vault/projects/ai-portfolio-assistant-{es,en}.md` permanece intacto, pero `getPublicProjects()` lo excluye de las rutas públicas y del sitemap mientras la funcionalidad está desactivada. El proyecto comercial de agentes IA es un trabajo profesional independiente y continúa siendo visible como caso de estudio.

La implementación original del Worker queda en `api/src/experimental_worker.py`. El punto de entrada público `api/src/worker.py` solo sirve la aplicación mínima de `public_portfolio_app.py`, con `/health`. Chat, administración y OpenAPI responden 404. No importa ni inicializa el pipeline de IA.

En desarrollo local, `frameworks_and_drivers/fastapi_app.py` mantiene la fábrica y los adaptadores para los tests, pero su montaje experimental está comentado y exporta la aplicación pública. `create_app()` sigue disponible de forma explícita para pruebas aisladas.

## Configuración preservada

- Frontend experimental: `PUBLIC_API_URL` (URL, nunca una clave secreta).
- API: nombres documentados en `api/.env.example`, incluidos `ALLOWED_ORIGINS`, `API_KEY`, `ADMIN_API_KEY`, límites de sesión y rate limit. No se copian valores a esta nota.
- Bindings de Cloudflare preservados: `AI`, `VECTORIZE`, `DB` en `api/wrangler.jsonc`.
- Dependencias experimentales conservadas en `api/pyproject.toml`, su lockfile y los módulos existentes. No se agregó un SDK de IA al frontend.

## Probar sin alterar la rama del portfolio

1. Usar un checkout separado de `codex/experimental-ai-chatbot`. No cambiar de rama sobre este checkout con trabajo pendiente.
2. Instalar las dependencias existentes de `apps/web` y `api`.
3. Ejecutar primero los tests offline; no se requieren llamadas a modelos para estos tests.
4. Probar el frontend contra una API de desarrollo. Para Workers, usar bindings de prueba y revisar su configuración antes de iniciar pruebas que puedan consumir servicios.
5. Mantener las credenciales en archivos locales ignorados. No copiar `.env` a la web, commits o documentación.

## Reintegrar cuando esté listo

No es necesario restaurar toda la rama antigua: eso también recuperaría el diseño y posicionamiento previos. Integrar únicamente las mejoras del asistente que se quieran conservar.

1. Trabajar desde una rama nueva basada en `codex/portfolio-profesional` con los cambios guardados.
2. Probar los cambios experimentales y aplicar sus commits o archivos de forma selectiva.
3. Para reactivar el Worker, reemplazar el contenido de `api/src/worker.py` por `from experimental_worker import Default`. No basta con descomentar el import encima de la clase pública, porque esa clase lo sobrescribiría.
4. Si se necesita la API local experimental, restaurar las dos líneas comentadas que crean `_local_traces` y `app` al final de `fastapi_app.py`, y quitar el alias público de ese módulo. La fábrica existente sigue siendo la responsable de construir sus rutas.
5. Restaurar en las páginas los imports comentados de `Chatbot` y `getCopy`, y montar el componente con `copy={getCopy(locale).chat}` y `locale={locale}`. Recuperar los estilos del widget y revisar que no reemplacen el nuevo sistema visual.
6. Decidir explícitamente si se vuelve a publicar el caso de estudio del asistente y modificar `getPublicProjects()` si corresponde.
7. Actualizar los tests de desactivación para reflejar la nueva decisión de producto. Conservar comprobaciones de carga diferida, ausencia de secretos y falta de llamadas automáticas.
8. Comprobar accesibilidad, respuestas sin evidencia, fallos de red y límites antes de fusionar. El despliegue se realiza como una acción posterior independiente.

## Comprobaciones de la rama sin asistente

Desde `apps/web`:

```sh
npm run check
npm test
npm run build
npm run test:site
npm run preview -- --host 127.0.0.1 --port 4321
```

Desde `api`:

```sh
.venv/Scripts/python.exe -m pytest -q -m "not token"
```

El comando del intérprete corresponde al entorno local de Windows; en otros entornos, usar `uv run pytest -q -m "not token"`.
