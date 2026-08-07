# Partner Onboarding — Vertical Slice

A resumable 3-step self-service onboarding wizard: a partner submits their details, validates their
external Provider integration, and goes live. Backend owns the session state; the frontend renders
whatever step the backend says the partner is on.

> _(One paragraph here at the end: what actually works, in plain terms.)_

---

## Stack, and why

| Layer | Choice | Version (developed/tested against) | Reason |
|---|---|---|---|
| Backend | Python · FastAPI · SQLAlchemy · Alembic | Python 3.14.6 · FastAPI 0.141.1 · SQLAlchemy 2.0.51 · Alembic 1.19.0 | _(fill in — the brief allows the strongest stack; state why this shows better judgment than a struggling Node slice)_ |
| DB | PostgreSQL | 16.14 (Homebrew, local) | Required. Migrations via Alembic. |
| Frontend | React · Vite · TypeScript · TanStack Query | _pinned once scaffolded in Phase 4_ | _(fill in — server state belongs in a query cache, which is what makes resume trivial)_ |
| Contract | OpenAPI → `openapi-typescript` | | Frontend types are generated from the backend schema, never hand-written. |

Full pinned backend dependency list (exact, not ranges — reproducibility matters more than staying
on latest for a take-home): [`backend/requirements.txt`](./backend/requirements.txt). Key ones:
`fastapi==0.141.1`, `sqlalchemy==2.0.51`, `alembic==1.19.0`, `pydantic==2.13.4`,
`pydantic-settings==2.15.0`, `psycopg[binary]==3.3.4`, `httpx==0.28.1`.

---

## Running it locally

### Prerequisites

- Python 3.12+ (developed/tested on 3.14.6)
- Node 20+ (frontend not yet scaffolded — exact version to be pinned in Phase 4)
- PostgreSQL 15+ running locally (developed/tested on 16.14, installed via `brew install postgresql@16`)

### 1. Database

```bash
# if installed via Homebrew, its bin dir isn't on PATH by default:
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

brew services start postgresql@16   # if not already running
createdb partner_onboarding
createdb partner_onboarding_test    # used by the backend test suite, see Tests below
```

### 2. Backend

```bash
cd backend
cp .env.example .env          # adjust DATABASE_URL if needed
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload  # http://localhost:8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql://localhost/partner_onboarding` | Postgres connection |
| `PROVIDER_TIMEOUT_SECONDS` | `5` | Timeout for the Provider call |
| `PARTNER_ID` | `demo-partner` | Hardcoded identity (auth is out of scope) |

---

## Exercising the Provider failure modes

The mock Provider is driven by magic `apiKey` values, so every path can be reproduced from the UI:

| `apiKey` | Provider responds | What the app should do |
|---|---|---|
| `valid-key` | `200 valid` + items | Items persisted, partner can advance |
| `partial-key` | `200 partial` + items + warnings | Warnings surfaced, partner chooses whether to continue |
| `invalid-key` | `200 invalid` + reason | Reason shown, partner returns to step 1 to correct credentials |
| `timeout-key` | `503` / timeout | Treated as transient; retry button; session state untouched |

Any other value behaves like `valid-key`. _(Adjust if you change this.)_

---

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/sessions` | Create or resume the session for the current partner |
| `GET` | `/sessions/{id}` | Current status + all data collected so far (this is what drives resume) |
| `POST` | `/sessions/{id}/details` | Submit step 1 |
| `POST` | `/sessions/{id}/validate` | Trigger integration validation (idempotent, retry-safe) |
| `POST` | `/sessions/{id}/go-live` | Finalize (idempotent, transactional) |

Interactive docs at `http://localhost:8000/docs`.

### Session states

```
DRAFT → DETAILS_OK → VALIDATING → VALIDATED → LIVE
                          ├→ INVALID     (recoverable: correct credentials)
                          └→ UNAVAILABLE (recoverable: retry)
```

Every mutating endpoint checks the current state before transitioning and returns `409` if the
transition is not legal from that state.

---

## Assumptions

> _Explicit assumptions I made where the brief left room. Stating these is part of the deliverable._

- **A single trusted partner.** Auth is out of scope, so the partner identity is hardcoded
  (`PARTNER_ID`) and one onboarding session belongs to it.
- **One active session per partner.** `POST /sessions` returns the existing in-progress session
  rather than creating a second one. _(Adjust if you decide otherwise.)_
- **Credentials are stored as provided.** No encryption at rest — noted as deferred below rather
  than half-implemented.
- **The Provider is the source of truth for items**; we persist a snapshot from the last successful
  validation, we do not reconcile continuously.
- _(fill in any others you hit while building)_

---

## Design decisions & trade-offs

> _The section they actually read. Explain the "why", including what you gave up._

**Backend owns the step; the client never does.**
_(fill in — what this buys, what it costs in round-trips)_

**Idempotency approach.**
_(fill in — how duplicate submits and duplicate go-live are handled, and why you chose this over an idempotency-key header / upsert / other)_

**`invalid` vs `unavailable` are separate states.**
_(fill in — why collapsing them into "error" would be wrong for the user and for retries)_

**The Provider call happens outside the DB transaction.**
_(fill in — why holding a transaction across a slow HTTP call is a problem)_

**Type safety across the boundary.**
_(fill in — generated types vs shared package vs hand-written DTOs, and the trade-off you accepted)_

**State stored as a single status column vs an event log.**
_(fill in)_

---

## Deliberately deferred

> Naming these is worth more than half-building them.

- **Auth / login** — out of scope per the brief; a hardcoded partner identity is used.
- **Real Provider integration** — mock only, per the brief.
- **Docker / CI / deployment** — out of scope; local run only.
- **Visual polish** — minimal styling on purpose; function over form.
- **Surfacing validation attempt history in the UI** — every `validate` call writes an insert-only
  row to `validation_log` (outcome, detail, timestamp), but no endpoint reads it yet. Kept it
  write-only rather than building the read side, since the brief doesn't ask for it; the schema is
  already there if time allows a "last 3 attempts" panel.
- _(fill in the ones you actually hit: e.g. credential encryption at rest, concurrent-session handling, background job for validation, pagination of items, structured logging/observability)_

For each of the above I noted _why_ it was safe to skip inside a 4–6 hour budget rather than
silently omitting it.

---

## With another day

_(3–5 concrete items, in priority order. This shows you know what "done" would look like.)_

1. A `GET /sessions/{id}/validation-log` (or embed the last N in `GET /sessions/{id}`) endpoint plus
   a small UI panel — the data already exists in `validation_log`, this is a read path away.
2.
3.

---

## Tests

```bash
cd backend && pytest              # requires partner_onboarding_test DB, see step 1 above
cd frontend && npx playwright test  # happy path + resume-after-reload
```

**Current state (Phase 1):** `backend/tests/test_schema.py` — 6 tests against a real Postgres DB
covering DB-level defaults and constraints (CHECK on `status`/`outcome`, `UNIQUE` on `partner_id`
and `(session_id, external_id)`, cascade delete). State machine transitions, idempotency, and
Provider failure-mode tests land in Phase 2/5 once `state_machine.py` and the routes exist — this
line will be updated as they're added rather than left describing tests that don't exist yet.

What the full suite is covered and why once complete:

- **State machine** — legal transitions succeed, illegal ones return `409`.
- **Idempotency** — submitting a step twice and calling go-live twice do not duplicate or corrupt.
- **Provider failure modes** — all four outcomes, including that `unavailable` leaves the session retryable.
- **Consistency** — a failure mid go-live leaves no partial state.
- **E2E** — full flow, and a mid-flow reload that resumes at the correct step.

Coverage was not a goal; these are the behaviours the design depends on.

---

## AI usage

Claude Code was used throughout. See [`AI_LOG.md`](./AI_LOG.md) for the curated decision log and
[`ai-log/`](./ai-log) for the raw session transcripts.
