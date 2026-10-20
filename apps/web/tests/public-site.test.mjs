import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const dist = path.resolve('dist');
const readPage = (route) => fs.readFileSync(path.join(dist, route, 'index.html'), 'utf8');

for (const locale of ['es', 'en']) {
  test(`${locale}: professional sections, working anchors and student attribution`, () => {
    const html = readPage(locale);
    for (const id of ['work', 'experience', 'teaching', 'skills', 'services', 'process', 'about', 'contact']) {
      assert.ok(html.includes(`id="${id}"`), `missing ${id}`);
    }
    assert.match(html, locale === 'es' ? /ESTRUCTURAS DE DATOS/i : /DATA STRUCTURES/i);
    assert.match(html, /testing/i);
    assert.match(html, locale === 'es' ? /desarrollo pertenece a los estudiantes/i : /development belongs to the students/i);
    const styles = fs.readdirSync(path.join(dist, '_astro')).filter(name => name.endsWith('.css')).map(name => fs.readFileSync(path.join(dist, '_astro', name), 'utf8')).join('');
    assert.match(styles, /prefers-reduced-motion/);
    assert.match(html, new RegExp(`href="/${locale === 'es' ? 'en' : 'es'}/"`));
    assert.match(html, /mailto:dev@nachosanchez.com.ar/);
    assert.ok(fs.existsSync(path.join(dist, 'resume/nacho-sanchez-ai-engineer.pdf')));
    for (const match of html.matchAll(/href="(#[^"]+)"/g)) {
      assert.ok(html.includes(`id="${match[1].slice(1)}"`), `broken anchor ${match[1]}`);
    }
  });

  test(`${locale}: case studies exist and public pages do not mount the assistant`, () => {
    const html = readPage(locale);
    const routes = [...html.matchAll(new RegExp(`href="(/${locale}/projects/[^"#]+/)"`, 'g'))].map(match => match[1]);
    assert.ok(new Set(routes).size >= 4, 'freelance and educational projects must be discoverable');
    for (const page of [html, ...routes.map(route => readPage(route.slice(1)))]) {
      assert.doesNotMatch(page, /data-chat-open|data-suggestion|class="assistant-widget"|<textarea|\/v1\/chat/);
      assert.doesNotMatch(page, /Preguntar a AI|Ask AI|Abrir asistente|Open assistant/);
    }
    assert.ok(!fs.existsSync(path.join(dist, locale, 'projects/ai-portfolio-assistant/index.html')));
  });
}

test('public bundles do not include experimental chatbot transport', () => {
  for (const name of fs.readdirSync(path.join(dist, '_astro'))) {
    if (!name.endsWith('.js')) continue;
    const bundle = fs.readFileSync(path.join(dist, '_astro', name), 'utf8');
    assert.doesNotMatch(bundle, /\/v1\/chat|chat-session|chat-visitor|PUBLIC_API_URL/);
  }
});
