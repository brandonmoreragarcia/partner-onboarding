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

## 9. AI log obligation

Every working session gets exported to `ai-log/` and the notable decisions get recorded in `AI_LOG.md` **as they happen**, before the commit. Code and log are committed together. Never sanitize a transcript beyond removing real secrets.
