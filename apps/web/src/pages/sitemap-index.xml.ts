import { getProjects } from "../shared/content/projects";

export const GET = () => {
  const urls = ["https://nachosanchez.com.ar/en/", "https://nachosanchez.com.ar/es/", ...(["en", "es"] as const).flatMap((locale) => getProjects(locale).map((project) => `https://nachosanchez.com.ar/${locale}/projects/${project.slug}/`))];
  const body = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.map((url) => `<url><loc>${url}</loc></url>`).join("")}</urlset>`;
  return new Response(body, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
};
