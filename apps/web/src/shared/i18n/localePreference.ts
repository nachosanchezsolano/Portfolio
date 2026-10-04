export type PreferredLocale = 'en' | 'es';
export const localeStorageKey = 'portfolio-language';
type Reader = { getItem(key: string): string | null };
type Writer = { setItem(key: string, value: string): void };
export function resolveLocale(saved: string | null, languages: readonly string[]): PreferredLocale {
  if (saved === 'es' || saved === 'en') return saved;
  for (const language of languages) {
    const locale = language.toLowerCase().split('-')[0];
    if (locale === 'es' || locale === 'en') return locale;
  }
  return 'en';
}
export function readPreferredLocale(storage?: Reader): string | null {
  try { return (storage ?? globalThis.localStorage)?.getItem(localeStorageKey) ?? null; }
  catch { return null; }
}
export function rememberLocale(locale: PreferredLocale, storage?: Writer): void {
  try { (storage ?? globalThis.localStorage)?.setItem(localeStorageKey, locale); }
  catch { /* Navigation remains available when storage is blocked. */ }
}
