import en from "./locales/en.json";
import es from "./locales/es.json";

export type Locale = "en" | "es";
export const translations = { en, es } as const;
export const getCopy = (locale: Locale = "en") => translations[locale];
