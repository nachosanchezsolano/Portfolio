import type { ChatMessage } from '../entities/chat';
import { requestChat, safeVisitorId } from './chatTransport';
const apiUrl = (import.meta.env.PUBLIC_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://porfolio-api.nachosanchez.com.ar')).replace(/\/+$/, '');
let sessionId: string = crypto.randomUUID();
const visitorId = safeVisitorId();
export const resetChatSession = () => { sessionId = crypto.randomUUID(); };
export type ChatRequestOptions = { signal?: AbortSignal; locale?: 'en' | 'es'; pageContext?: string; requestId?: string };
export async function askPortfolio(message: string, options: ChatRequestOptions = {}): Promise<ChatMessage> {
  const payload = await requestChat(apiUrl, { message, session_id: sessionId, visitor_id: visitorId, locale: options.locale ?? 'en', page_context: options.pageContext ?? null, request_id: options.requestId ?? crypto.randomUUID() }, options);
  sessionId = payload.session_id;
  return { id: crypto.randomUUID(), role: 'assistant', content: payload.message, sources: payload.sources, intent: payload.intent, sessionId, observationId: payload.observation_id ?? undefined };
}
