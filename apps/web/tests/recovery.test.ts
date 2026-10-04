import { test } from 'node:test';
import assert from 'node:assert/strict';
import { PendingQuestion, retryDelay } from '../src/features/home/services/chatRecovery.ts';

test('a lost response or rate limit keeps one logical question and request id', () => {
  const pending = new PendingQuestion();
  const first = pending.begin('Question');
  const retry = pending.begin('Question');
  assert.equal(retry.requestId, first.requestId);
  assert.equal(retry.isNew, false);
  assert.equal(retryDelay('rate'), 60_000);
  pending.complete();
  const next = pending.begin('Question');
  assert.notEqual(next.requestId, first.requestId);
  assert.equal(next.isNew, true);
});
