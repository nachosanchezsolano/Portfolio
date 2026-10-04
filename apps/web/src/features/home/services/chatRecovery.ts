import type { ErrorKind } from './chatTransport.ts';
export class PendingQuestion {
  private pending: { question: string; requestId: string } | null = null;
  begin(question: string) {
    const isNew = this.pending?.question !== question;
    if (isNew) this.pending = { question, requestId: crypto.randomUUID() };
    return { ...this.pending!, isNew };
  }
  complete() { this.pending = null; }
}
export const retryDelay = (kind: ErrorKind) => kind === 'rate' ? 60_000 : kind === 'pending' ? 5_000 : 0;
