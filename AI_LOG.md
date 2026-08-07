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
| 01 | [`ai-log/01-design.md`](./ai-log/01-design.md) | Schema, state machine, API contract | _(fill in)_ |
| 02 | [`ai-log/02-backend.md`](./ai-log/02-backend.md) | Endpoints, Provider client, transactions | _(fill in)_ |
| 03 | [`ai-log/03-frontend.md`](./ai-log/03-frontend.md) | Wizard, resume, validation states | _(fill in)_ |
| 04 | [`ai-log/04-tests.md`](./ai-log/04-tests.md) | Backend tests + e2e | _(fill in)_ |

---

## Decision log

> One entry per notable moment. Keep them short and honest — including the ones where I was wrong.
> Tag each as **accepted / rejected / redirected**. Delete this instruction block before submitting.

### D1 — Backend stack: Python instead of Node · _redirected_

**Context.** The brief prefers Node/TypeScript.

**What the AI proposed.** _(fill in)_

**What I decided.** Python + FastAPI, because it is where I can show senior-level judgment inside a
4–6h budget, and the brief explicitly allows the strongest stack. Type safety across the stack is
preserved by generating frontend types from the OpenAPI schema rather than hand-writing them.

**Why it matters.** _(fill in)_

---

### D2 — _(title)_ · _accepted / rejected / redirected_

**Context.**

**What the AI proposed.**

**What I did.**

**Why.**

---

### D3 — _(title)_ · _accepted / rejected / redirected_

**Context.**

**What the AI proposed.**

**What I did.**

**Why.**

---

## Moments where I caught the AI being wrong

> The section the brief asks for explicitly. Be specific: what exactly was wrong, how I noticed,
> what I did. Vague entries are worth nothing here.

**1. _(fill in)_**
- What it produced:
- How I noticed:
- Fix:

**2. _(fill in)_**
- What it produced:
- How I noticed:
- Fix:

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
