# CLAUDE.md — Partner Onboarding Take-Home

Project rules for AI-assisted work on this repo. Read this before writing any code.

The full assignment — requirements, deliverables and evaluation criteria — is in `BRIEF.md`
(local, gitignored). Read it when a question is about *what is required* rather than *how we build it*.

---

## 1. What we are building

A resumable, 3-step self-service partner onboarding wizard:

1. **Details** — partner submits company name + Provider credentials (`accountId`, `apiKey`).
2. **Validate integration** — backend calls a mock Provider, persists the result and the returned items.
3. **Review & go live** — partner reviews and finalizes; the session becomes `LIVE`.

The partner can leave at any point and resume later at the correct step with their data intact.

**Time budget: 4–6 hours.** A smaller correct slice beats a broad broken one. When in doubt, cut scope and document the decision in the README rather than rushing.

## 2. Stack

- **Backend:** Python + FastAPI + SQLAlchemy + Alembic (migrations) + Pydantic.
- **DB:** PostgreSQL.
- **Frontend:** React + Vite + TypeScript + TanStack Query.
- **Types:** generated from the FastAPI OpenAPI schema via `openapi-typescript`. Never hand-write frontend types that mirror backend models.
- **Tests:** pytest (backend), Playwright (2 e2e tests max).

Node was the suggested stack; Python is the strongest stack here and the brief explicitly allows it. This rationale belongs in the README.

## 3. Architecture rules (non-negotiable)

- **The backend owns the session state.** The frontend never decides which step the user is on — it reads `status` from `GET /sessions/{id}` and renders accordingly.
- **No client-side persistence of flow state.** No localStorage, no sessionStorage, no step counter in React state. Resume works because the state lives in Postgres.
- **Explicit state machine.** A single `status` column with a fixed set of values. Every mutating endpoint asserts the current status allows the transition, and returns `409` otherwise. Never mutate from an unexpected state.
- **Idempotency everywhere.** Submitting the same step twice, or calling go-live twice, must be safe: the second call returns the current session, it does not duplicate rows or corrupt state.
- **Go-live is transactional.** All writes for the finalize step happen in one DB transaction. Partial commits are a bug.
- **Never hold a DB transaction open across the Provider HTTP call.** Call the Provider outside the transaction, then persist the outcome.
- **`invalid` and `unavailable` are different outcomes.** `invalid` = bad credentials, user must correct them. `unavailable` = transient (503/timeout), same credentials, safe to retry. A generic `except` that collapses them is a bug, not a shortcut.
- GUIA-ARRANQUE.md and BRIEF.md are local references, not deliverables. (do not add to commits or push)

## 4. State machine

```
DRAFT ──submit details──> DETAILS_OK ──trigger validation──> VALIDATING
VALIDATING ──200 valid|partial──> VALIDATED ──go live (TX)──> LIVE
VALIDATING ──200 invalid─────────> INVALID  ──corrected details──> DETAILS_OK
VALIDATING ──503/timeout─────────> UNAVAILABLE ──retry──> VALIDATING
```

`LIVE` is terminal. `INVALID` and `UNAVAILABLE` are recoverable and must never leave orphaned or half-written data.

## 5. Code rules

**Backend**

- Pydantic models at every boundary (request bodies, responses, env config). No untyped dicts crossing layers.
- State transition logic lives in one module, not scattered across route handlers. Routes validate input and delegate.
- Typed error responses (`{code, message}`), consistent across endpoints.
- Provider client has an explicit timeout and returns a typed result union — never raises raw HTTP errors into the route.
- Migrations via Alembic only. No `create_all` in application code.

**Frontend**

- One `useQuery(['session', id])` is the source of truth. The wizard `switch`es on `status`.
- Mutations call `invalidateQueries` on success; do not optimistically advance the step.
- Disable submit/retry controls while a mutation or validation is in flight.
- All five validation states are visibly distinct: `pending`, `valid`, `partial`, `invalid`, `unavailable`.
- components with custom hooks where the logic lives in the hooks, not the components.

**General**

- No dependency gets added without a reason that can be stated in one sentence.
- No speculative abstraction, no features outside the brief. Out of scope: auth, real integrations, Docker/K8s, CI, visual polish.
- Small, focused commits. Typecheck + tests green before moving to the next feature.
- Each phase gets its own branch (e.g. `phase-1-schema-design`). When the phase is done, merge directly into `main` and push — no pull request. This is a solo take-home; PR review overhead doesn't apply here.
- **"Move to phase X" is not authorization to commit phase X.** Wait for an explicit go-ahead before committing/merging each phase's work, even once the branch-per-phase workflow above is established — ask again each time rather than assuming continued license from an earlier "commit and push."
- code should be divided into smaller, more manageable files and components, lets do the one file per feature approach.

## 6. Mock Provider

In-process fake, triggered by magic `apiKey` values:

| `apiKey` | Response |
|---|---|
| `valid-key` | `200 {status: "valid", items: [...]}` |
| `partial-key` | `200 {status: "partial", items: [...], warnings: [...]}` |
| `invalid-key` | `200 {status: "invalid", reason: "..."}` |
| `timeout-key` | `503` / no response |

These must be documented in the README so reviewers can exercise every path.

## 7. Testing rules

Test what is being evaluated, not coverage:

- State machine transitions, including rejected ones (`409` from a wrong state).
- Idempotency: duplicate step submit, duplicate go-live.
- All four Provider outcomes, including that `unavailable` leaves the session retryable.
- Go-live rollback: failure mid-transaction leaves no partial state.
- E2E (Playwright, max 2): full happy path; reload mid-flow resumes at the correct step.

Do not write tests that only assert the mock was called.

## 8. How to work with me (the AI)

- **Offer options before implementing.** For non-obvious backend decisions, give 2–3 approaches with trade-offs and a recommendation for a 4–6h slice. I choose.
- **Be critical when asked to review.** Do not say code is fine by default. Name concurrency issues, crash-recovery gaps, and unstated assumptions.
- **Explain backend code plainly.** I am strongest in frontend. If I cannot explain a piece of backend code, it does not ship — simplify it or explain it.
- **Flag scope creep.** If I ask for something outside the brief or beyond the time budget, say so before building it.
- **Reproduce before fixing.** For any bug, write the failing test first.
- **Cross-check against `BRIEF.md` before closing out each phase.** `BRIEF.md` is the source of truth for what's actually required — go through its requirements/evaluation-criteria line by line against what was just built, name any gap explicitly (even a deferred one), don't just assert compliance.

## 9. AI log obligation

Every working session gets exported to `ai-log/` and the notable decisions get recorded in `AI_LOG.md` **as they happen**, before the commit. Code and log are committed together. Never sanitize a transcript beyond removing real secrets.

**Log each decision the moment it's made, not batched at phase end.** Any time the user picks between options presented via `AskUserQuestion` or direct discussion, or redirects an AI proposal, add the `AI_LOG.md` entry (Context + what the AI proposed, at minimum) before starting the next task — don't wait to be asked, don't wait for a natural pause. If one gets missed, the user pointing it out is itself worth a moment; catch up immediately rather than at the next commit.

## 10. Locked schema & API contract (Phase 1 design)

Decided and implemented (`backend/app/models/`, `backend/alembic/versions/`). Do not re-derive or
silently change any of this — if a later block needs something different, say so explicitly and
update this section.

**`sessions`**

| Column | Type | Constraints |
|---|---|---|
| `id` | `UUID` | PK, app-generated (`uuid.uuid4()`) |
| `partner_id` | `TEXT` | `NOT NULL UNIQUE` — target of the `POST /sessions` upsert |
| `status` | `VARCHAR(20)` | `NOT NULL DEFAULT 'DRAFT'`, `CHECK` against the 7 state values (SQLAlchemy `Enum(..., native_enum=False, create_constraint=True)` — **`create_constraint=True` is required**, SQLAlchemy 2.0 defaults it to `False` and silently drops the CHECK) |
| `company_name`, `account_id`, `api_key` | `TEXT` | nullable; overwritten in place on resubmit, never a new row |
| `last_error` | `TEXT` | nullable; persisted (not response-only) so `INVALID`/`UNAVAILABLE` survive reload/restart; cleared on successful resubmit or successful validation |
| `warnings` | `JSONB` | `NOT NULL DEFAULT '[]'`; the `valid`/`partial` discriminator at `status=VALIDATED` (empty → valid, non-empty → partial) since the state machine itself has no `PARTIAL` value |
| `created_at`/`updated_at` | `TIMESTAMPTZ` | `NOT NULL DEFAULT now()` |

`apiKey` is accepted on input, never echoed back in any response.

**`items`** — FK `session_id → sessions.id ON DELETE CASCADE`, `external_id TEXT NOT NULL`, `name TEXT NOT NULL`, `UNIQUE(session_id, external_id)`. Re-validation deletes and reinserts rows atomically with the session's status update — no upsert-by-diff.

**`validation_log`** — insert-only, not part of any API response. `session_id` FK cascade, `outcome` (`valid|partial|invalid|unavailable`, same CHECK-via-Enum pattern), `detail` nullable, `created_at`, index on `(session_id, created_at)`. Written by `apply_validation_result` in the *same* transaction as the `sessions`/`items` writes for that call. Exists for debugging/audit and a future "last 3 attempts" UI feature — not read by any endpoint yet.

**State machine module contract** (`app/state_machine.py`, functions own their own commits):

```python
def submit_details(db, session_id, payload: DetailsIn) -> SessionRow
    # legal from: DRAFT, DETAILS_OK, INVALID → DETAILS_OK
def claim_validation(db, session_id) -> tuple[SessionRow, bool]
    # conditional UPDATE ... WHERE status IN ('DETAILS_OK','UNAVAILABLE')
    # INVALID is deliberately NOT claimable here — the §4 diagram only draws
    # INVALID -> DETAILS_OK (via corrected details), never INVALID -> VALIDATING directly
    # claimed=True  -> caller must call the Provider
    # claimed=False -> caller must NOT call the Provider (already VALIDATING -> 200 current state; illegal state -> 409)
def apply_validation_result(db, session_id, result: ProviderResult) -> SessionRow
    # one transaction: delete+insert items, update status/warnings/last_error, INSERT validation_log row
def go_live(db, session_id) -> SessionRow
    # conditional UPDATE WHERE status='VALIDATED'; 0 rows + already LIVE -> idempotent replay; else 409
```

The `validate` route is the one place that deliberately opens **two separate, short-lived DB
sessions** with the Provider HTTP call between them holding no DB connection at all. Do not
"simplify" this back to one session — that reintroduces holding a connection open across the
Provider call, which §3 forbids.

**API contract** (`app/schemas/`, wire format `camelCase` via Pydantic `alias_generator`, status values stay `UPPER_SNAKE`):

| Endpoint | Legal from | Result | Status codes |
|---|---|---|---|
| `POST /sessions` | — | get-or-create by `partner_id` (`INSERT ... ON CONFLICT DO NOTHING`) | `201` new, `200` resumed |
| `GET /sessions/{id}` | any | read | `200`, `404` |
| `POST /sessions/{id}/details` | `DRAFT, DETAILS_OK, INVALID` | → `DETAILS_OK` | `200`, `404`, `409`, `422` |
| `POST /sessions/{id}/validate` | `DETAILS_OK, UNAVAILABLE` (+`VALIDATING`→no-op replay) | → `VALIDATED\|INVALID\|UNAVAILABLE` | `200` (all reachable outcomes incl. duplicate-in-flight), `404`, `409` (from `DRAFT/INVALID/VALIDATED/LIVE`) |
| `POST /sessions/{id}/go-live` | `VALIDATED` (+`LIVE`→no-op replay) | → `LIVE` | `200`, `404`, `409` |

Errors are always `{code, message}`.

**Provider client contract** (Phase 3): `ProviderResult = ProviderValid | ProviderPartial | ProviderInvalid | ProviderUnavailable`, each a Pydantic model. `ProviderClient.validate()` never raises HTTP exceptions into callers — timeout/connect errors and `503` both map to `ProviderUnavailable`. Timeout via `PROVIDER_TIMEOUT_SECONDS`.

**Flagged decisions, not to be silently revisited:**
- `TEXT`+`CHECK` over native Postgres `ENUM` — Alembic's `ALTER TYPE ... ADD VALUE` story is awkward; `CHECK` keeps DB-level safety with a one-line migration to change.
- Items in a separate table (not JSONB) — real relational schema, queryable, worth the delete+insert cost on retry.
- `POST /sessions` returns `201`/`200` depending on create-vs-resume — communicates which case occurred for near-zero cost.
- No arrow back to `DETAILS_OK` from `VALIDATED`/`UNAVAILABLE` in the given state diagram — only from `INVALID`. Staying strict to the diagram; "edit after validating" is a "with another day" candidate, not silently added scope.
- `validation_log` is write-only today — do not build a read endpoint for it without checking the time budget first; it was deliberately kept out of the API contract.

**Known Alembic false positive — do not blindly apply:** `alembic revision --autogenerate` will
propose `op.drop_constraint('session_status', ...)` / `op.drop_constraint('validation_outcome', ...)`
on essentially every run, even with no model changes. Postgres stores the CHECK constraint text
normalized (`status::text = ANY (ARRAY[...]::text[])`) while SQLAlchemy recompiles the `Enum`'s
constraint fresh each time for comparison — the two never match textually even though they're
semantically identical, so Alembic's naive text-diff always flags it. Always read an autogenerated
migration before applying it; if the only ops are dropping/recreating these two constraints with no
other real change, delete the generated file rather than run it.

**Local dev environment (this machine):** Postgres 16 via Homebrew (`brew services start postgresql@16`), DB `partner_onboarding`, trust-auth on `localhost`, no password. Python 3.14.6, backend deps pinned exactly in `backend/requirements.txt` (see README for exact versions) — pins exist so `alembic upgrade head` and everything downstream stays reproducible, not because loose ranges were a problem encountered.
