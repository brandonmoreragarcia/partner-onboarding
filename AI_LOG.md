# AI Interaction Log

> **How to read this file.** This is the curated layer: an index of the working sessions plus the
> specific moments where I accepted, rejected, or redirected the AI, and why. The full unedited
> transcripts live in [`ai-log/`](./ai-log). Nothing has been cleaned up beyond removing local
> paths and real credentials.

---

## How I worked

**Tooling.** Devin Desktop as the editor, Claude Code as the only AI agent. I deliberately did not
mix in a second agent (Devin's own Cascade / autocomplete) so that the entire history of AI
involvement would be captured in one traceable log. Anything typed by hand is in the git history;
anything AI-assisted is in the transcripts.

**My split of confidence.** I am strongest in frontend. There I directed the AI with my own opinion
and overrode it when I disagreed. On the backend I am less experienced, so I deliberately switched
modes: instead of accepting proposals, I asked for options with trade-offs, ran adversarial reviews
on the generated code, and verified behaviour by executing it rather than by reading it. Both modes
are visible below.

**Loop per feature.** Ask for options → choose and state why → implement → adversarial review
("what breaks under concurrency / crash / retry?") → reproduce any issue with a test → commit code
and log together.

---

## Session index

| # | Transcript | Focus | Outcome |
|---|---|---|---|
| 01 | [`ai-log/01-design.md`](./ai-log/01-design.md) | Schema, state machine, API contract | 7 decisions (D1–D7), all schema/migration/package layout — see file |
| 02 | [`ai-log/02-backend.md`](./ai-log/02-backend.md) | Endpoints, Provider client, transactions | D8 + a real identity-map bug caught via curl, not code review — see file |
| 03 | [`ai-log/03-frontend.md`](./ai-log/03-frontend.md) | Wizard, resume, validation states | _(not started)_ |
| 04 | [`ai-log/04-tests.md`](./ai-log/04-tests.md) | Backend tests + e2e | _(not started)_ |

---

## Decision log

> The full per-decision log (Context / what the AI proposed / what I did / why) lives in each
> phase's own file under [`ai-log/`](./ai-log), not here — see the Session index above. Keeping it
> per-phase instead of centralized here so this file stays a lean index as more phases land.
> Tag each entry as **accepted / rejected / redirected**.

---

## Moments where I caught the AI being wrong

> The section the brief asks for explicitly. Be specific: what exactly was wrong, how I noticed,
> what I did. Vague entries are worth nothing here.

**1. `validate` response showed stale (empty) `items` despite the DB being correct**
- What it produced: `apply_validation_result` loaded the session with items eagerly loaded via
  `selectinload` *before* mutating the items table, then re-loaded it *after* committing — but
  SQLAlchemy's identity map returned the same cached collection instead of the fresh one. The
  `POST /validate` response showed `items: []` right after a successful `valid-key` validation,
  while a `GET` immediately after on the same session showed the real 2 items.
- How I noticed (the AI, during its own verification pass — not caught by me first): curl'd the
  live endpoint after implementing it, per the "reproduce before fixing" rule in CLAUDE.md, rather
  than trusting that reading the code back was enough.
- Fix: `.execution_options(populate_existing=True)` on the re-fetch query. Full repro script and
  before/after output in `ai-log/02-backend.md`.

**2. API contract allowed `validate` from `INVALID` directly, contradicting the state diagram**
- What it produced: Phase 1's first design pass listed `validate` as claimable from
  `DETAILS_OK, INVALID, UNAVAILABLE` — but CLAUDE.md §4's diagram only draws `INVALID -> DETAILS_OK`
  (via corrected details), never `INVALID -> VALIDATING` directly.
- How I noticed (the AI, cross-checking its own design doc against the diagram before building the
  ERD walkthrough): re-reading §4 while drawing the state diagram for the walkthrough artifact.
- Fix: corrected `claim_validation`'s claimable states before any route code existed, so it never
  shipped as a bug. Confirmed live in Phase 2 verification: `validate` from `INVALID` now returns
  `409`.

---

## Review questions I used

These are the prompts I reached for repeatedly, especially on backend code where I could not rely on
intuition alone:

- "Give me 2–3 approaches with trade-offs and recommend one for a 4–6 hour slice."
- "Be critical of this code. What happens if two requests hit this endpoint at the same time?"
- "What happens if the process dies right after the Provider call but before the commit?"
- "What did you assume that I never told you?"
- "Is this transition safe to retry? Show me the concrete case that breaks it."
- "If the Provider takes 30 seconds, what is happening to the DB connection meanwhile?"
- "Are `invalid` and `unavailable` actually handled differently, or does the same `except` swallow both?"
- "What here is unnecessary complexity for this scope? Remove it."
- "Explain this as if I did not know SQLAlchemy — I need to be able to defend it."

---

## Reflection

> 3–6 sentences, written at the end. What the AI was genuinely good at, where it needed steering,
> what I would do differently next time, and how I decided when to trust it.

_(fill in)_
