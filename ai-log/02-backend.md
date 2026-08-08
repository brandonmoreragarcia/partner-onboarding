# Session 02 — Backend core: endpoints, Provider client, transactions

---

### D9 — Status-transition constants moved to `constants.py` · _redirected_
`_DETAILS_LEGAL_FROM`/`_VALIDATE_CLAIMABLE_FROM` were private tuples inside `state_machine.py`; moved to a shared `app/constants.py` since routes/tests need them too.

### D10 — `_get_or_404`'s comments trimmed to 1-2 liners · _redirected_
Two bug-explaining comments had grown to 11 lines combined; condensed to 2 lines each, pointing here for the full story.

### D11 — `apply_validation_result`'s `isinstance` chain replaced with a dispatch dict · _accepted_
Compared a `match`/`case` alternative against a dispatch-dict-of-handlers in full code; chose the dispatch dict, then moved the 4 handlers out to `app/provider_result_handlers.py` so `state_machine.py` stays focused on transitions.

### Code review findings — no code change
- **`go_live` concurrency: no race exists.** The precondition and write are one atomic `UPDATE ... WHERE status='VALIDATED' RETURNING id` — Postgres's row lock closes the window before it can open. Proved with two real threads racing the same session; now a permanent test.
- **`scalar_one_or_none()` usage: correct as written.** All 3 call sites are scoped by a unique column, and `selectinload` (not `joinedload`) can't multiply row counts — safe by construction, not luck.

