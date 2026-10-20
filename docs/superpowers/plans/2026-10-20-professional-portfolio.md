# Professional portfolio implementation plan

**Goal:** Apply the approved Substrata portfolio brief to the existing bilingual Astro site.
**Architecture:** Preserve the Astro/static Markdown architecture and all project evidence. Introduce shared bilingual portfolio copy and an isolated visual stylesheet. Preserve the assistant on a local branch and disconnect both public UI and API entry points.
**Spec:** User-approved portfolio prompt in the current conversation, 2026-10-20.
**Constraints:** No framework migration, invented claims, student images, remote publishing, secret changes, or edits to the two pre-existing profile modifications. Work in the user's existing checkout on `codex/portfolio-profesional`; backup branch `codex/experimental-ai-chatbot` records committed pre-change code at b3dfcf1.

## Tasks
- [x] Inspect repository, public evidence and baseline frontend tests (9 passed). Create preservation and working branches.
- [x] Add built-site regression checks for bilingual sections, actual project links, no chatbot bundles or entry points; observe failure against the old build.
- [x] Implement editorial black/acid-green homepage, bilingual content, accessible mobile navigation, project previews, services, teaching, skills, process and contact.
- [x] Match case studies and entry page to the new design, retain experimental case-study source without publishing the integrated assistant project.
- [x] Preserve experimental Worker and disconnect public chat routes, with request-level offline regression tests.
- [x] Build, run frontend/API checks and browser QA on desktop/mobile and keyboard. Statically verify reduced-motion CSS; browser media emulation was not available. Document reactivation and actual verification results.

## Review focus
- No automatic assistant imports or outbound model calls on homepage/case studies.
- No misattribution of student work or fabricated project images.
- No broken anchors, project URLs, locale switches or résumé links.
- Mobile menu Escape/focus behavior, long headlines and reduced motion.
- Experimental AI code and existing profile edits remain recoverable.

## Execution ledger
- User approved the complete design and explicitly requested implementation; execute in this session without repeating design approval.
- Branch preservation contains the committed assistant implementation. Two unrelated, pre-existing profile edits remain in the working directory and are not committed or overwritten.
- Built-site checks initially failed against the previous implementation (missing teaching sections, active chatbot). After implementation, 5/5 passed.
- API baseline: 79 tests passed; new public request tests initially failed because the public module did not exist. Final result: 82 passed. The isolated-import test was corrected to run from `api/src`, matching the actual import root.
- Added only development type definitions, aligned with CI's Node 22. TypeScript modules pass `npm run check`; Astro compilation checks page syntax, without adding the optional Astro language-server checker.
- Final independent read-only review found one Important issue: an open mobile modal remained inert/scroll-locked after entering the desktop breakpoint. Reproduced in browser; added two regression tests (observed RED→GREEN), extracted the breakpoint listener, and verified the same browser scenario closes the dialog, releases scrolling and focuses desktop navigation. Final frontend unit suite: 11/11; built-site suite: 5/5; API: 82/82.
- Review scope exclusions: existing profile changes, experimental assistant internals, résumé contents and remote production checks were left untouched. These are outside the approved local redesign; production still requires a separate deployment action.
- Browser checks: Spanish desktop 1440×1000, mobile 390×844, Spanish/English 320×740 and English tablet 768×1024; no horizontal overflow. Mobile opening/Escape/anchors and educational case-study navigation verified. Final console check returned no warnings/errors.
- No supplied project screenshots were available; previews use neutral typographic project notes. Student and confidential project images remain unpublished.
- The user subsequently authorized commit and push of `codex/portfolio-profesional`. The two pre-existing profile edits are excluded. Deployment and merging into main remain outside this Git delivery.
