# Session 01 — Design: schema, state machine, API contract

> Decision log for Phase 1. Full raw transcript (via `/export`) goes in this same file or
> alongside it — see `AI_LOG.md` for how this fits into the overall log.

---

### D1 — Backend stack: Python instead of Node · _redirected_

**Context.** The brief prefers Node/TypeScript.

**What the AI proposed.** AI proposed Node/TypeScript at the beggining, which is a stack I could work on, but feel more comfortable with Python code as it was part of the stack from my latest work experience.

**What I decided.** Python + FastAPI, because it is where I can show senior-level judgment inside a
4–6h budget, and the brief explicitly allows the strongest stack. Type safety across the stack is
preserved by generating frontend types from the OpenAPI schema rather than hand-writing them.

---

### D2 — Provider items: separate `items` table vs JSONB on `sessions` · _accepted_

**Context.** Phase 1 design — where validated Provider items get persisted.

**What the AI proposed.** Two options via `AskUserQuestion` with a concrete schema/model/response
example for each: a separate `items` table with an FK to `session_id`, or a JSONB `items` column
directly on `sessions`.

**What I did.** I chose the separate `items` table with an FK to `session_id`.

**Why.** This approach provides better data normalization and allows for more complex queries and relationships in the future. It also makes it easier to add additional metadata or indexes to the items table if needed.

---

### D3 — Session identity: `UNIQUE` constraint on `partner_id` · _accepted_

**Context.** No auth; a single hardcoded `PARTNER_ID`. Needed a rule for "one session per partner"
and how `POST /sessions` resumes vs. creates.

**What the AI proposed.** A DB-level `UNIQUE` constraint on `sessions.partner_id` with
`POST /sessions` as an atomic `INSERT ... ON CONFLICT DO NOTHING` upsert, vs. a query-for-latest
non-terminal session with no constraint.

**What I did.** I chose the DB-level `UNIQUE` constraint on `sessions.partner_id` with
`POST /sessions` as an atomic `INSERT ... ON CONFLICT DO NOTHING` upsert.

**Why.** This approach ensures data integrity at the database level and prevents race conditions
where multiple requests might try to create a new session simultaneously. It also provides a clear
and consistent way to handle the "one session per partner" rule.

---

### D4 — Concurrent `POST /validate` calls return `200` with current state, not `409` · _accepted_

**Context.** What should happen if `validate` is called a second time while the first call is still
in flight (status already `VALIDATING`).

**What the AI proposed.** Two options with worked example request/response pairs: `200` with the
session's current (`VALIDATING`) state as-is and no second Provider call, vs. `409` treating it as
an illegal transition.

**What I did.** I chose the `200` with the session's current (`VALIDATING`) state as-is and no second Provider call.

**Why.** This approach provides a better user experience by not blocking the user from seeing the current state of the session. It also prevents race conditions where multiple requests might try to validate the same session simultaneously.

---

### D5 — `status` column: `TEXT` + `CHECK` constraint over a native Postgres `ENUM` · _accepted_

**Context.** How to model the 7-value session status column at the DB level.

**What the AI proposed.** Three options: a native Postgres `ENUM` type, `VARCHAR` + `CHECK`
constraint (via SQLAlchemy `Enum(native_enum=False)`), or a lookup table / unconstrained text.

**What I did.** I chose the `VARCHAR` + `CHECK` constraint (via SQLAlchemy `Enum(native_enum=False)`).

**Why.** This approach provides a good balance between type safety and flexibility. It allows for easy validation of the status values while still being able to add new values if needed in the future.

---

### D6 — `validation_log`: insert-only audit table · _redirected_

**Context.** Whether to keep any history of validation attempts, or only the latest result on the
session row.

**What the AI proposed.** Initially recommended "only the latest result." When asked whether a log
could still be useful for debugging/audit, proposed a cheaper middle ground: an insert-only
`validation_log` table (`session_id`, `outcome`, `detail`, `created_at`), written in the same
transaction as `apply_validation_result`, not read by any endpoint yet.

**What I did.** I chose the insert-only audit table approach.

**Why.** This approach provides a good balance between cost and functionality. It allows for easy debugging and audit trails while still being a relatively simple implementation.

---

### D7 — `models.py`/`schemas.py`: entity-per-file split · _accepted_

**Context.** Both files were still small (~100 and ~40 lines) but CLAUDE.md's own rule is "one file
per feature," and Phase 2's `state_machine.py` will import heavily from both — worth settling the
shape before more code depends on it.

**What the AI proposed.** Two layouts: (1) entity-per-file — one file per SQLAlchemy table /
matching Pydantic group (`session.py`, `item.py`, `validation_log.py` on the models side;
`session.py`, `item.py`, `errors.py` on the schemas side), 7 files total, maximum discoverability.
(2) aggregate-boundary split — `session.py` keeps `SessionRow`+`ItemRow` together since they're
never independently meaningful (same lifecycle, same transactions), `validation_log.py` split out
as a genuinely separate concern (audit trail); 5 files total. Recommended (2) as the smaller move
for what's still fairly small code.

**What I did.** I chose the entity-per-file split approach.

**Why.** Maximum discoverability at any future scale — one obvious file per table — was worth more to me than minimizing file count now, especially since Phase 2's `state_machine.py` will import from these heavily.

---

## Verification evidence (Phase 1)

- `alembic upgrade head` runs clean on a freshly dropped/recreated database.
- CHECK constraints confirmed at the DB level with a raw SQL insert that Postgres rejects
  (`session_status`, `validation_outcome`) — not just asserted from reading the code.
- 6 schema-level pytest tests passing against a real Postgres test DB (defaults, both CHECK
  constraints, `UNIQUE` on `partner_id` and `(session_id, external_id)`, cascade delete).
- Caught and fixed: `SQLAlchemy 2.0`'s `Enum(create_constraint=...)` defaults to `False`, which
  silently dropped the CHECK constraint the D5 decision was for — found by querying `pg_constraint`
  directly instead of trusting a successful migration run.
- Caught and fixed: the API contract initially allowed `validate` from `INVALID` directly, which
  the state diagram in `CLAUDE.md` §4 never draws (only `INVALID → DETAILS_OK`) — corrected before
  it became a Phase 2 bug.
- Caught and documented: `alembic revision --autogenerate` permanently false-positives on dropping
  both CHECK constraints (Postgres normalizes the stored constraint text differently than
  SQLAlchemy recompiles it) — not a real regression, but will resurface on every future autogenerate
  run unless someone knows to check `CLAUDE.md` first.
