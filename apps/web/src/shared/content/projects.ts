import fs from 'node:fs';
import path from 'node:path';
import { load, JSON_SCHEMA } from 'js-yaml';
export interface PortfolioProject {
  slug: string; locale: 'en' | 'es'; title: string; status: string;
  technologies: string[]; period: string; role: string; body: string;
  evidence: { github?: string; demo?: string };
}
const projectsDirectory = path.resolve(process.cwd(), '../../knowledge-base/vault/projects');
function safeUrl(value: unknown): string | undefined {
  if (typeof value !== 'string') return undefined;
  try { const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password ? url.href : undefined; }
  catch { return undefined; }
}
function month(value: unknown, locale: 'en' | 'es'): string {
  if (typeof value !== 'string' || !/^\d{4}-(0[1-9]|1[0-2])$/.test(value)) return '';
  return new Intl.DateTimeFormat(locale, { month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${value}-01T00:00:00Z`)).replace('.', '');
}
export function parseProjectSource(fileName: string, source: string): PortfolioProject {
  const match = /^---\n([\s\S]*?)\n---(?:\n|$)([\s\S]*)$/.exec(source.replace(/\r\n/g, '\n'));
  if (!match) throw new Error(`Missing frontmatter: ${fileName}`);
  const data = load(match[1], { schema: JSON_SCHEMA }) as Record<string, any>;
  const locale = fileName.endsWith('-es.md') ? 'es' : 'en';
  const slug = fileName.replace(/-(en|es)\.md$/, '');
  const start = month(data.period?.start, locale), end = month(data.period?.end, locale);
  const period = start ? `${start} — ${end || (locale === 'es' ? 'Actualidad' : 'Present')}` : '';
  const educational = ['lessions', 'aquanova'].includes(slug);
  const status = slug === 'ai-sales-chatbot' ? (locale === 'es' ? 'Pruebas cerradas · Proyecto confidencial' : 'Closed testing · Confidential project') : educational ? (locale === 'es' ? 'Proyecto educativo' : 'Educational project') : data.status === 'published' ? (locale === 'es' ? 'Publicado' : 'Published') : String(data.status ?? '');
  const role = educational ? (locale === 'es' ? 'Docente y mentor' : 'Teacher and mentor') : (locale === 'es' ? 'Desarrollo de punta a punta' : 'End-to-end development');
  return { slug, locale, title: String(data.title ?? ''), status, technologies: Array.isArray(data.technologies) ? data.technologies.filter((x: unknown) => typeof x === 'string') : [], period, role, body: match[2].trim(), evidence: { github: safeUrl(data.evidence?.github), demo: safeUrl(data.evidence?.demo) } };
}
export const getProjects = (locale: 'en' | 'es' = 'en') => fs.readdirSync(projectsDirectory)
  .filter(fileName => fileName.endsWith(`-${locale}.md`))
  .filter(fileName => /^---\r?\n[\s\S]*?^visibility:\s*public\s*$/m.test(fs.readFileSync(path.join(projectsDirectory, fileName), 'utf8').split(/\r?\n---/)[0]))
  .map(fileName => parseProjectSource(fileName, fs.readFileSync(path.join(projectsDirectory, fileName), 'utf8')))
  .sort((a, b) => a.title.localeCompare(b.title));
