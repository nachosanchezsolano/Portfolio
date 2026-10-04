export type ErrorKind = 'network' | 'timeout' | 'cancelled' | 'rate' | 'session' | 'validation' | 'invalid' | 'pending';
export class ChatRequestError extends Error {
  kind: ErrorKind;
  constructor(kind: ErrorKind) { super(kind); this.name = 'ChatRequestError'; this.kind = kind; }
}
export type ChatResponse = { message: string; sources: string[]; intent: 'general' | 'recruiter' | 'technical'; session_id: string; observation_id?: string | null };
type Storage = { getItem(key: string): string | null; setItem(key: string, value: string): void };
export function safeVisitorId(storage?: Storage): string {
  const generated = crypto.randomUUID();
  try {
    const store = storage ?? globalThis.localStorage;
    const id = store?.getItem('portfolio-chat-visitor-id') || generated;
    store?.setItem('portfolio-chat-visitor-id', id);
    return id;
  } catch { return generated; }
}
type Options = { signal?: AbortSignal; timeoutMs?: number; fetcher?: (url: string, init: RequestInit) => Promise<Response> };
export async function requestChat(apiUrl: string, payload: Record<string, unknown>, options: Options = {}): Promise<ChatResponse> {
  if (options.signal?.aborted) throw new ChatRequestError('cancelled');
  const controller = new AbortController();
  let timedOut = false;
  const timer = setTimeout(() => { timedOut = true; controller.abort(); }, options.timeoutMs ?? 15_000);
  const abort = () => controller.abort();
  options.signal?.addEventListener('abort', abort, { once: true });
  try {
    const response = await (options.fetcher ?? fetch)(`${apiUrl}/v1/chat`, {
      method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(payload), signal: controller.signal,
    });
    if (!response.ok) {
      let detail = '';
      try { detail = String((await response.json()).detail ?? ''); } catch { /* Classify by status. */ }
      throw new ChatRequestError(response.status === 429 ? 'rate' : response.status === 409 ? 'pending' : response.status === 400 ? (/chat session.*more than/i.test(detail) ? 'session' : 'validation') : 'network');
    }
    let value: unknown;
    try { value = await response.json(); } catch { throw new ChatRequestError('invalid'); }
    const data = value as Partial<ChatResponse> | null;
    if (!data || typeof data.message !== 'string' || !data.message.trim() || !Array.isArray(data.sources) || !data.sources.every(x => typeof x === 'string') || !['general', 'recruiter', 'technical'].includes(data.intent ?? '') || typeof data.session_id !== 'string') throw new ChatRequestError('invalid');
    return data as ChatResponse;
  } catch (error) {
    if (error instanceof ChatRequestError) throw error;
    throw new ChatRequestError(timedOut ? 'timeout' : options.signal?.aborted ? 'cancelled' : 'network');
  } finally {
    clearTimeout(timer); options.signal?.removeEventListener('abort', abort);
  }
}
