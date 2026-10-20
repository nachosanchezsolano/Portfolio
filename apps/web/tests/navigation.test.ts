import { test } from 'node:test';
import assert from 'node:assert/strict';
import { closeMobileMenuOnDesktop } from '../src/shared/navigation/mobileNavigation.ts';

class Breakpoint extends EventTarget {
  matches = false;
  setDesktop(value: boolean) { this.matches = value; this.dispatchEvent(new Event('change')); }
}

test('a mobile menu stays open on mobile but closes when desktop navigation appears', () => {
  const breakpoint = new Breakpoint();
  let closeCount = 0;
  const dialog = { open: true, close() { this.open = false; closeCount++; } };
  closeMobileMenuOnDesktop(dialog, breakpoint);
  breakpoint.setDesktop(false);
  assert.equal(dialog.open, true);
  breakpoint.setDesktop(true);
  assert.equal(dialog.open, false);
  assert.equal(closeCount, 1);
  breakpoint.setDesktop(true);
  assert.equal(closeCount, 1, 'do not close an already closed dialog');
});

test('desktop initialization releases an existing modal and cleanup removes the listener', () => {
  const breakpoint = new Breakpoint();
  breakpoint.matches = true;
  const dialog = { open: true, close() { this.open = false; } };
  const cleanup = closeMobileMenuOnDesktop(dialog, breakpoint);
  assert.equal(dialog.open, false);
  cleanup();
  dialog.open = true;
  breakpoint.setDesktop(true);
  assert.equal(dialog.open, true);
});
