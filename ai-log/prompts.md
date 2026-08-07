# Prompts I used

The recurring prompts I reached for while building this. They are here because *how* I directed the
AI is part of what I want to show — especially on the backend, where I am less experienced and chose
to work by asking for options and reviewing adversarially rather than by accepting proposals.

Full transcripts are in this directory; the curated decisions are in [`../AI_LOG.md`](../AI_LOG.md).

---

## 1 · Data model — options before implementation

> Before writing any code, I want to settle the data model. Give me 2–3 options for each of these,
> with trade-offs, and recommend one for a 4–6 hour slice:
>
> 1. How to model `status` — a Postgres enum, a text column with a CHECK constraint, or something else?
> 2. Where the Provider items live — a separate `provider_item` table, or JSONB on the session row?
> 3. Whether to keep a history of validation attempts (a `validation_attempt` table) or only the latest result.
>
> Don't write the migration yet. I'll pick first.

## 2 · Crash recovery

> If the server dies between marking the session `VALIDATING` and persisting the Provider's response,
> the session is stuck in `VALIDATING` forever. Walk me through what that means for the user, and give
> me 2–3 ways to handle it ranked by cost for a 4–6 hour budget — including the option of accepting it
> and documenting it as a known limitation. Which would you pick and why?

## 3 · Concurrency

> Two `go-live` requests arrive at the same time. Both read the session as `VALIDATED` before either
> writes, so both think they may proceed. Show me exactly where the race is in my current code, then
> give me 2–3 fixes with trade-offs (row-level lock, unique constraint, optimistic version column, or
> something else). Is this worth solving inside this scope, or is documenting it the senior call?

## 4 · Adversarial review — before accepting any backend code

> Be critical of this code — do not tell me it looks fine. Specifically:
>
> - What happens if two requests hit this endpoint simultaneously?
> - What happens if the process dies right after the Provider call but before the commit?
> - Is a DB transaction held open across the Provider HTTP call anywhere?
> - Are `invalid` and `unavailable` genuinely handled as different outcomes, or does one `except` collapse them?
> - Can any path leave the session in a state that isn't in my state machine?
> - What did you assume that I never told you?

## 5 · Clarity and scope

> Explain this as if I didn't know SQLAlchemy — I need to be able to defend it in an interview.
> Then tell me what here is unnecessary complexity for this scope and remove it.

---

## Rules I applied to myself

- **Options before implementation.** On any non-obvious backend decision, ask for 2–3 approaches with
  trade-offs, then choose and state why. The choice is mine; the menu is the AI's.
- **Run the adversarial review before accepting code, not at the end of the day.** Late review means
  rewriting; early review means designing.
- **Reproduce before fixing.** When a review turns up a real problem, the failing test lands first, so
  the finding is evidence in the repo rather than a claim in a log.
- **Nothing ships that I cannot explain.** If I can't defend a piece of code, it gets simplified or
  explained until I can — or it doesn't go in.
