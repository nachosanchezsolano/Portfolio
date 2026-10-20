/** Release the modal's focus trap and scroll lock when desktop navigation takes over. */
export function closeMobileMenuOnDesktop(
  dialog: Pick<HTMLDialogElement, 'open' | 'close'>,
  breakpoint: EventTarget & { readonly matches: boolean },
): () => void {
  const closeIfDesktop = () => {
    if (breakpoint.matches && dialog.open) dialog.close();
  };
  breakpoint.addEventListener('change', closeIfDesktop);
  closeIfDesktop();
  return () => breakpoint.removeEventListener('change', closeIfDesktop);
}
