const INLINE_PATTERN = /(\*\*[^*\n]+\*\*|`[^`\n]+`|\*[^*\n]+\*)/g;

const appendInlineContent = (parent: HTMLElement, content: string): void => {
  let cursor = 0;

  for (const match of content.matchAll(INLINE_PATTERN)) {
    const index = match.index ?? 0;
    parent.append(document.createTextNode(content.slice(cursor, index)));

    const token = match[0];
    const element = document.createElement(
      token.startsWith("**") ? "strong" : token.startsWith("`") ? "code" : "em",
    );
    const delimiterLength = token.startsWith("**") ? 2 : 1;
    element.textContent = token.slice(delimiterLength, -delimiterLength);
    parent.append(element);
    cursor = index + token.length;
  }

  parent.append(document.createTextNode(content.slice(cursor)));
};

const createTextBlock = (tag: "p" | "li", content: string): HTMLElement => {
  const element = document.createElement(tag);
  appendInlineContent(element, content);
  return element;
};

/** Render the assistant's supported Markdown subset without injecting model HTML. */
export const formatAssistantMessage = (content: string): DocumentFragment => {
  const fragment = document.createDocumentFragment();
  const lines = content.replace(/\r\n?/g, "\n").split("\n");
  let paragraphLines: string[] = [];
  let list: HTMLOListElement | HTMLUListElement | null = null;

  const flushParagraph = (): void => {
    if (paragraphLines.length > 0) {
      fragment.append(createTextBlock("p", paragraphLines.join(" ")));
      paragraphLines = [];
    }
  };

  const closeList = (): void => {
    if (list) fragment.append(list);
    list = null;
  };

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const fence = line.match(/^```([\w.+-]*)\s*$/);

    if (fence) {
      flushParagraph();
      closeList();
      const codeLines: string[] = [];
      index += 1;
      while (index < lines.length && !/^```\s*$/.test(lines[index])) {
        codeLines.push(lines[index]);
        index += 1;
      }
      const pre = document.createElement("pre");
      const code = document.createElement("code");
      if (fence[1]) code.dataset.language = fence[1];
      code.textContent = codeLines.join("\n");
      pre.append(code);
      fragment.append(pre);
      continue;
    }

    const unordered = line.match(/^\s*[-*]\s+(.+)$/);
    const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
    if (unordered || ordered) {
      flushParagraph();
      const tag = ordered ? "OL" : "UL";
      if (!list || list.tagName !== tag) {
        closeList();
        list = document.createElement(ordered ? "ol" : "ul");
      }
      list.append(createTextBlock("li", (unordered ?? ordered)?.[1] ?? ""));
      continue;
    }

    closeList();
    if (line.trim()) paragraphLines.push(line.trim());
    else flushParagraph();
  }

  flushParagraph();
  closeList();
  return fragment;
};
