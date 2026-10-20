# Cloudflare Workers Builds: raíz del repositorio

## Causa del error ENOENT

El comando `npm run build` se estaba ejecutando en `/opt/buildhome/repo`, pero el único `package.json` estaba en `apps/web`. Por eso la compilación no llegaba a ejecutar Astro ni detectaba las dependencias del frontend.

## Configuración desde la raíz

Para el Worker del frontend `portfolio-web`:

| Campo | Valor |
| --- | --- |
| Root directory | `/` (raíz del repositorio) |
| Build command | `npm run build` |
| Deploy command | `npx wrangler deploy` |
| Node.js | 22.19 o posterior |
| Assets | `apps/web/dist`, definido en `wrangler.jsonc` |

El nuevo script raíz ejecuta `npm ci` dentro de `apps/web` usando su lockfile, y luego ejecuta allí la compilación de Astro. El `package-lock.json` raíz permite que el entorno detecte npm aunque la raíz no tenga dependencias propias.

La configuración raíz es exclusivamente para los assets estáticos del portfolio: no despliega la API Python ni incorpora sus archivos al sitio.

## Alternativa: frontend como directorio raíz

La configuración anterior sigue siendo válida: root directory `apps/web`, build `npm run build`, deploy `npx wrangler deploy`. En este caso Cloudflare instala las dependencias del frontend y usa `apps/web/wrangler.jsonc`, cuyo directorio de assets es `./dist`.

No se cambian las rutas de origen del contenido Markdown: ambos modos ejecutan Astro con `apps/web` como directorio de trabajo, de modo que los casos de estudio pueden seguir leyendo `knowledge-base/vault/projects`.

## Rama y reintento

El build debe usar un commit que contenga estos archivos. La corrección se entrega en `codex/portfolio-profesional`; si Cloudflare está conectado a otra rama, selecciona la rama correcta o integra la corrección mediante el flujo habitual antes de reintentar.

No se modificaron las opciones de tu cuenta de Cloudflare ni se ejecutó un despliegue remoto desde esta sesión.

## Verificación de la corrección

Se reprodujo primero el ENOENT ejecutando `npm run build` desde la raíz original. Después se probó una copia limpia del commit del portfolio, sin `node_modules`, agregando únicamente los nuevos archivos raíz:

- `npm ci` desde la raíz: aprobado.
- `npm run build` desde la raíz: instala las dependencias bloqueadas del frontend y genera las 13 páginas.
- `npm --prefix apps/web run check`: sin errores.
- `npm --prefix apps/web run test:site`: cinco pruebas aprobadas.
- `npx --yes wrangler@4.125.0 deploy --dry-run`: configuración válida y 37 archivos encontrados en `apps/web/dist`; no publica.

GitHub Actions también ejecuta ahora la compilación del frontend desde la raíz y detecta cambios en los manifiestos y en la configuración raíz. La validación local se ejecutó en Windows; el siguiente build remoto confirma el entorno de Cloudflare.

Referencia: https://developers.cloudflare.com/workers/ci-cd/builds/configuration/
