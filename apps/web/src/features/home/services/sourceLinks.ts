const projects: Record<string, [string, string]> = {
  'ai-portfolio-assistant': ['Asistente AI del portfolio', 'AI portfolio assistant'],
  'grupo-eurosa': ['Grupo Eurosa', 'Grupo Eurosa'],
  'ai-sales-chatbot': ['Chatbot comercial con IA', 'AI sales chatbot'],
  'aquanova': ['Aquanova', 'Aquanova'],
  'estudio-chingon': ['Estudio Chingón', 'Estudio Chingón'],
  'lessions': ['Lessions', 'Lessions'],
};
export function sourceLinks(sources: readonly string[], locale: 'en' | 'es') {
  const links = new Map<string, { href: string; label: string }>();
  for (const source of sources) {
    const slug = /^projects\/([a-z0-9-]+)-(?:en|es)\.md$/.exec(source)?.[1];
    let href: string | undefined, label: string | undefined;
    if (slug && projects[slug]) {
      href = `/${locale}/projects/${slug}/`; label = projects[slug][locale === 'es' ? 0 : 1];
    } else if (/^profile\/(?:profile-(?:en|es)|principles|now)\.md$/.test(source)) {
      const principles = source === 'profile/principles.md';
      href = `/${locale}/#${principles ? 'principles' : 'about'}`;
      label = locale === 'es' ? (principles ? 'Principios' : 'Perfil profesional') : (principles ? 'Principles' : 'Professional profile');
    }
    if (href && label) links.set(href, { href, label });
  }
  return [...links.values()];
}
