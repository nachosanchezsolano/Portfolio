import fs from "node:fs";
import path from "node:path";

export interface PortfolioProject {
  slug: string;
  locale: "en" | "es";
  title: string;
  status: string;
  technologies: string[];
  period: string;
  body: string;
}

const projectsDirectory = path.resolve(process.cwd(), "../../knowledge-base/vault/projects");

const readField = (frontmatter: string, field: string) => {
  const match = frontmatter.match(new RegExp(`^${field}:\\s*(.+)$`, "m"));
  return match?.[1]?.trim().replace(/^['"]|['"]$/g, "") ?? "";
};

const readList = (frontmatter: string, field: string) => {
  const block = frontmatter.match(new RegExp(`^${field}:\\n((?:\\s+- .+\\n?)+)`, "m"))?.[1] ?? "";
  return [...block.matchAll(/^\s+- (.+)$/gm)].map((match) => match[1].trim());
};

const parseProject = (fileName: string): PortfolioProject => {
  const source = fs.readFileSync(path.join(projectsDirectory, fileName), "utf8");
  const [, frontmatter = "", body = ""] = source.split("---");
  const locale = fileName.endsWith("-es.md") ? "es" : "en";
  const slug = fileName.replace(/-(en|es)\.md$/, "");
  return {
    slug,
    locale,
    title: readField(frontmatter, "title"),
    status: readField(frontmatter, "status"),
    technologies: readList(frontmatter, "technologies"),
    period: readField(frontmatter, "period"),
    body: body.trim(),
  };
};

export const getProjects = (locale: "en" | "es" = "en") =>
  fs.readdirSync(projectsDirectory)
    .filter((fileName) => fileName.endsWith(`-${locale}.md`))
    .map(parseProject)
    .sort((a, b) => a.title.localeCompare(b.title));
