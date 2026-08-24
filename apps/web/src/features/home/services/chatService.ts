import type { ChatMessage } from "../entities/chat";

type ChatResponse = { message: string; sources?: string[]; session_id?: string };

const apiUrl = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";
const sessionId = crypto.randomUUID();

export const askPortfolio = async (message: string, signal?: AbortSignal): Promise<ChatMessage> => {
  const response = await fetch(`${apiUrl}/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
    signal,
  });

  if (!response.ok) throw new Error("No pude conectar con la base de conocimiento.");
  const data = (await response.json()) as ChatResponse;
  return { id: crypto.randomUUID(), role: "assistant", content: data.message };
};
