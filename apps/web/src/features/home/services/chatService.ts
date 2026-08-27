import type { ChatIntent, ChatMessage } from "../entities/chat";

export type ChatResponse = {
  message: string;
  sources: string[];
  intent: ChatIntent;
  session_id: string;
};

const configuredApiUrl = import.meta.env.PUBLIC_API_URL || (
  import.meta.env.DEV
    ? "http://localhost:8000"
    : "https://porfolio-api.nachosanchez.com.ar"
);
const apiUrl = configuredApiUrl.replace(/\/+$/, "");
const sessionId = crypto.randomUUID();

const isChatResponse = (value: unknown): value is ChatResponse => {
  if (!value || typeof value !== "object") return false;
  const response = value as Record<string, unknown>;
  return (
    typeof response.message === "string" &&
    Array.isArray(response.sources) &&
    response.sources.every((source) => typeof source === "string") &&
    (response.intent === "general" || response.intent === "recruiter" || response.intent === "technical") &&
    typeof response.session_id === "string"
  );
};

export const askPortfolio = async (message: string, signal?: AbortSignal): Promise<ChatMessage> => {
  const response = await fetch(`${apiUrl}/v1/chat`, {
    method: "POST",
    headers: { "Accept": "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal,
  });

  if (!response.ok) throw new Error("No pude conectar con la base de conocimiento.");
  const payload: unknown = await response.json();
  if (!isChatResponse(payload)) throw new Error("La API devolvió una respuesta inválida.");
  return {
    id: crypto.randomUUID(),
    role: "assistant",
    content: payload.message,
    sources: payload.sources,
    intent: payload.intent,
    sessionId: payload.session_id,
  };
};
