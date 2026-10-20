# Portfolio QA — 20 de octubre de 2026

## Verificación automatizada

- `npm run check`: sin errores de TypeScript en los módulos `.ts`.
- `npm test`: 11 pruebas aprobadas, incluidas dos regresiones del menú responsive.
- `npm run build`: 13 páginas generadas (dos portadas, diez casos de estudio y entrada de idioma), más robots y sitemap.
- `npm run test:site`: 5 pruebas aprobadas sobre la salida generada, incluyendo contenido bilingüe, anchors, CV, rutas y ausencia del transporte del asistente.
- API offline: 82 pruebas aprobadas, incluyendo `/health` disponible, rutas experimentales 404 y ausencia de imports del pipeline de IA desde el punto de entrada público.
- `git diff --check`: sin errores de whitespace. Git informa únicamente la conversión normal de LF/CRLF del entorno.

## Verificación en navegador local

- 1440×1000: portada española y tipografía Anton/Inter/Space Mono cargada.
- 390×844: portada móvil, menú modal, foco inicial, Escape y enlace a Docencia.
- 320×740: ambas portadas sin desbordamiento horizontal.
- 768×1024: portada inglesa y caso de estudio de Aquanova, con atribución explícita a estudiantes.
- Menú abierto a 390px → 1024px: defecto detectado y corregido. El modal ahora se cierra, `aria-expanded` vuelve a false, se libera el scroll y el foco pasa a la navegación de escritorio.
- Consola final: sin errores ni advertencias.
- Movimiento reducido: reglas CSS presentes y verificadas estáticamente; no se emuló esta preferencia del sistema en el navegador.

Capturas: `portfolio-desktop.png` y `portfolio-mobile.png`.

## Ajuste posterior: selector de idioma

Se reemplazó el enlace EN/ES por un desplegable con el nombre completo del idioma, las dos opciones y el idioma actual identificado por texto, color y check. Se verificaron selección en ambos sentidos, conservación del caso de estudio Aquanova al cambiar de idioma, Enter, Escape, clic exterior y ausencia de desbordes del encabezado a 320px y 801px. TypeScript, compilación y las cinco pruebas del sitio generado pasan. Captura: `language-selector.png`.

Esta auditoría corresponde al checkout local. No se desplegaron los cambios ni se probaron servicios remotos de IA. Los enlaces externos conservan las URLs públicas existentes; no se enviaron formularios ni mensajes.
