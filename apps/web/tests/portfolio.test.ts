import { test } from 'node:test';
import assert from 'node:assert/strict';
import { resolveLocale, readPreferredLocale } from '../src/shared/i18n/localePreference.ts';
import { sourceLinks } from '../src/features/home/services/sourceLinks.ts';
import { ChatRequestError, requestChat, safeVisitorId } from '../src/features/home/services/chatTransport.ts';
import { chatStore } from '../src/features/home/stores/chatStore.ts';
import { getProjects, parseProjectSource } from '../src/shared/content/projects.ts';

test('locale remembers choices and respects ordered browser languages', () => {
  assert.equal(resolveLocale('es', ['en-US']), 'es');
  assert.equal(resolveLocale('invalid', ['fr', 'es-AR', 'en-US']), 'es');
  assert.equal(resolveLocale(null, ['en-GB', 'es']), 'en');
  assert.equal(resolveLocale(null, ['fr']), 'en');
  assert.equal(readPreferredLocale({ getItem() { throw new Error('blocked'); } }), null);
});
test('sources are unique allowlisted internal links', () => {
  assert.deepEqual(sourceLinks(['projects/grupo-eurosa-es.md', 'projects/grupo-eurosa-en.md', '../private.md', 'https://evil.test', 'profile/principles.md'], 'es').map(x => x.href), ['/es/projects/grupo-eurosa/', '/es/#principles']);
});
test('blocked storage still creates a visitor', () => {
  assert.ok(safeVisitorId({ getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } }));
});
test('session reset uses the translated welcome', () => {
  chatStore.reset('Welcome');
  chatStore.setError('failure');
  chatStore.reset('Hola');
  assert.equal(chatStore.getState().messages[0].content, 'Hola');
  assert.equal(chatStore.getState().error, null);
});
test('session and rate limits have distinct actionable errors', async () => {
  const payload = { message: 'q', session_id: 's', visitor_id: 'v', locale: 'en' };
  await assert.rejects(requestChat('http://local', payload, { fetcher: async () => new Response(JSON.stringify({detail: 'chat session cannot contain more than 5 messages'}), {status: 400}) }), (error: ChatRequestError) => error.kind === 'session');
  await assert.rejects(requestChat('http://local', payload, { fetcher: async () => new Response('{}', {status: 429}) }), (error: ChatRequestError) => error.kind === 'rate');
  await assert.rejects(requestChat('http://local', payload, { fetcher: async () => new Response('{}', {status: 200}) }), (error: ChatRequestError) => error.kind === 'invalid');
});
test('timeout and caller abort release the request', async () => {
  const fetcher = async (_: string, init: RequestInit) => new Promise<Response>((_, reject) => init.signal?.addEventListener('abort', () => reject(new Error('aborted'))));
  await assert.rejects(requestChat('http://local', {}, { fetcher, timeoutMs: 1 }), (error: ChatRequestError) => error.kind === 'timeout');
  const controller = new AbortController(); controller.abort();
  await assert.rejects(requestChat('http://local', {}, { fetcher, signal: controller.signal }), (error: ChatRequestError) => error.kind === 'cancelled');
});
test('project parser preserves nested YAML, dates and markdown separators', () => {
  const project = parseProjectSource('example-es.md', '---\ntitle: Example\nvisibility: public\nstatus: published\nperiod:\n  start: 2025-02\n  end: null\nevidence:\n  demo: https://example.com\n  github: javascript:alert(1)\ntechnologies: [Python, Astro]\n---\n# Body\n\n---\nMore');
  assert.equal(project.period, 'feb 2025 — Actualidad');
  assert.equal(project.evidence.demo, 'https://example.com/');
  assert.equal(project.evidence.github, undefined);
  assert.ok(project.body.includes('---\nMore'));
});

test('all existing public projects have valid YAML and accurate roles', () => {
  for (const locale of ['es', 'en'] as const) {
    const projects = getProjects(locale);
    assert.equal(projects.length, 6);
    assert.ok(projects.find(project => project.slug === 'grupo-eurosa')?.evidence.demo);
    assert.match(projects.find(project => project.slug === 'lessions')?.role ?? '', /mentor/);
    assert.match(projects.find(project => project.slug === 'aquanova')?.role ?? '', /mentor/);
    assert.ok(!projects.find(project => project.slug === 'grupo-eurosa')?.body.includes('\r'), 'normalize line endings so summaries are preserved');
  }
});
