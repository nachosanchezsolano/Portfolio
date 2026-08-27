export type ChatRole = "assistant" | "user";
export type ChatIntent = "general" | "recruiter" | "technical";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  sources?: string[];
  intent?: ChatIntent;
  sessionId?: string;
  observationId?: string;
};

export type ChatState = {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
};

export const createMessage = (role: ChatRole, content: string): ChatMessage => ({
  id: crypto.randomUUID(),
  role,
  content: content.trim(),
});

export const validateQuestion = (value: string, maxLength = 1200): string => {
  const question = value.trim();
  if (!question) throw new Error("Escribí una pregunta para comenzar.");
  if (question.length > maxLength) throw new Error(`La pregunta no puede superar los ${maxLength} caracteres.`);
  return question;
};
