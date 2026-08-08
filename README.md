# Partner Onboarding — Vertical Slice

A resumable 3-step self-service onboarding wizard: a partner submits their details, validates their
external Provider integration, and goes live. The backend owns all session state — the frontend
just reads `status` from the API and renders whatever step that implies. Reload, close the tab,
restart the server — the partner resumes exactly where they left off, because nothing about
progress lives in the browser.

- **Details** — company name + Provider credentials (`accountId`, `apiKey`).
- **Validate integration** — backend calls a mock Provider, persists the result and returned items.
- **Review & go live** — partner reviews and finalizes; the session becomes `LIVE`.

---

## Stack, and why

| Layer | Choice | Version (developed/tested against) | Reason |
|---|---|---|---|
| Backend | Python · FastAPI · SQLAlchemy · Alembic | Python 3.14.6 · FastAPI 0.141.1 · SQLAlchemy 2.0.51 · Alembic 1.19.0 | The brief allows the strongest stack over the suggested Node one. FastAPI + Pydantic gives request/response validation and an OpenAPI schema for free, which the frontend's types are generated from — a struggling Node slice would have cost more time than it saved on "familiarity." |
| DB | PostgreSQL | 16.14 (Homebrew, local) | Required by the brief. Migrations via Alembic. |
| Frontend | React · Vite · TypeScript · TanStack Query | React 19.2.8 · Vite 8.2 · TypeScript 6.0.2 · TanStack Query 5.101 | Server state (the session) belongs in a query cache, not component state — that's what makes "resume on reload" nearly free instead of something to hand-build. |
| Contract | OpenAPI → `openapi-typescript` | openapi-typescript 7.13 | Frontend types generated from the backend's own schema — never hand-written, so the two sides can't silently drift apart. |

Full pinned backend dependency list (exact, not ranges — reproducibility matters more than staying
on latest for a take-home): [`backend/requirements.txt`](./backend/requirements.txt). Key ones:
`fastapi==0.141.1`, `sqlalchemy==2.0.51`, `alembic==1.19.0`, `pydantic==2.13.4`,
`pydantic-settings==2.15.0`, `psycopg[binary]==3.3.4`, `httpx==0.28.1`.

---

## Running it locally

**Prerequisites:** Python 3.12+ (tested on 3.14.6) · Node 20+ (tested on 24.18) · PostgreSQL 15+
(tested on 16.14, `brew install postgresql@16`)

**1. Database**

```bash
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"   # if installed via Homebrew
brew services start postgresql@16                          # if not already running
createdb partner_onboarding
createdb partner_onboarding_test    # used by the backend test suite, see Tests below
```

**2. Backend**

```bash
cd backend
cp .env.example .env          # adjust DATABASE_URL if needed
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload  # http://localhost:8000
```

**3. Frontend**

```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

## Tests

```bash
cd backend && pytest                # requires partner_onboarding_test DB, see step 1 above
cd frontend && npx playwright test  # requires the backend running separately on :8000
```


**Environment variables**

| Variable | Where | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | `backend/.env` | `postgresql+psycopg://localhost/partner_onboarding` | Postgres connection (`+psycopg` selects psycopg3, matching `requirements.txt`) |
| `PROVIDER_TIMEOUT_SECONDS` | `backend/.env` | `5` | Timeout for the Provider call |
| `PARTNER_ID` | `backend/.env` | `demo-partner` | Hardcoded identity (auth is out of scope) |
| `VITE_API_BASE_URL` | `frontend/.env` (optional) | `http://localhost:8000` | Only needed if the backend isn't on the default host/port |

---

## Exercising the Provider failure modes

The mock Provider is driven by magic `apiKey` values, so every path can be reproduced from the UI:

| `apiKey` | Provider responds | What the app does |
|---|---|---|
| `valid-key` | `200 valid` + items | Items persisted, partner can advance |
| `partial-key` | `200 partial` + items + warnings | Warnings surfaced, partner chooses whether to continue |
| `invalid-key` | `200 invalid` + reason | Reason shown, partner returns to step 1 to correct credentials |
| `timeout-key` | `503` / timeout | Treated as transient; retry button; session state untouched |

Any other value behaves like `valid-key`.

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

**Session states**

```
DRAFT → DETAILS_OK → VALIDATING → VALIDATED → LIVE
                          ├→ INVALID     (recoverable: correct credentials)
                          └→ UNAVAILABLE (recoverable: retry)
```

Every mutating endpoint checks the current state before transitioning and returns `409` if the
transition is not legal from that state.

---

## Assumptions

- **A single trusted partner.** Auth is out of scope, so the partner identity is hardcoded
  (`PARTNER_ID`) and one onboarding session belongs to it.
- **One active session per partner.** `POST /sessions` returns the existing in-progress session
  rather than creating a second one.
- **Credentials are stored as provided.** No encryption at rest — noted under Deferred rather than
  half-implemented.
- **The Provider is the source of truth for items**; we persist a snapshot from the last successful
  validation rather than reconciling continuously.
- **`partial` items are still items.** A `partial` result's warnings flag specific items as
  suspect but don't exclude them — everything the Provider returns gets persisted and counted, and
  the partner decides whether to go live anyway. Silently dropping flagged items would be inventing
  behavior the Provider contract doesn't specify.

---

## Design decisions & trade-offs

**Backend owns the step; the client never does.** The frontend has no step counter, no
localStorage, no local flow state — it renders entirely off `status` from `GET /sessions/{id}`.
This is what makes resume-on-reload correct by construction instead of something to synchronize:
there's only one source of truth to get right. The cost is an extra round-trip on load compared to
optimistically rendering a locally-remembered step.

**Idempotency via conditional updates, not an idempotency-key header.** Duplicate `validate` or
`go-live` calls are handled with a conditional `UPDATE ... WHERE status = X ... RETURNING`: if the
row wasn't in the expected state, zero rows are affected and the caller gets back the current
session instead of an error (when the current state is the target state) or a `409` (when it
isn't). This piggybacks on the state machine that already has to exist, versus a separate
idempotency-key table that would duplicate that logic for no real benefit at this scope.

**`invalid` and `unavailable` are separate states, not a shared "error" bucket.** They imply
opposite actions: `invalid` means the credentials are wrong and the partner must go back and
correct them; `unavailable` means the same credentials are safe to retry as-is. Collapsing them
would either block a retryable case or invite resubmitting bad credentials.

**The Provider call happens outside any DB transaction.** `validate`'s route handler deliberately
opens two separate, short-lived DB sessions with the Provider HTTP call in between holding no DB
connection at all. A slow or hanging Provider call would otherwise hold a transaction (and a
connection) open for the duration — under load that's how a slow third party takes the whole app's
connection pool down with it.

**Types generated from the OpenAPI schema, not a shared package or hand-written DTOs.** FastAPI
already produces the schema for free from its own Pydantic models; `openapi-typescript` turns that
into frontend types with no duplication and no drift window. The trade-off is a manual regeneration
step (`npm run generate:api`) after backend schema changes, versus the build-tooling overhead a
shared monorepo package would add for two workspaces this small.

**A single `status` column, not an event log.** The brief's own state diagram is a fixed 7-value
machine, and every requirement (resumability, idempotency, `409` on illegal transitions) is
expressible as "read current status, conditionally update it." An event-sourced log would add
replay logic this scope never asked for. The one thing an event log would have made easier —
distinguishing `valid` from `partial` at the same `VALIDATED` status — is instead recovered from
the `warnings` column, which is documented as a deliberate compromise rather than silently reusing
one field for two meanings.

---

## Deliberately deferred
- **Surfacing validation attempt history in the UI** — every `validate` call writes an insert-only
  row to `validation_log` (outcome, detail, timestamp), but no endpoint reads it yet. Kept it
  write-only rather than building the read side, since the brief doesn't ask for it; the schema is
  already there if time allows a "last 3 attempts" panel.

---

## With another day

1. A `GET /sessions/{id}/validation-log` (or embed the last N in `GET /sessions/{id}`) endpoint plus
   a small UI panel — the data already exists in `validation_log`, this is a read path away.
2. Credential encryption at rest, plus a real auth layer to protect it behind — neither makes sense
   to add in isolation.
3. A background job for validation instead of a synchronous request/response — today the partner's
   request blocks on the Provider call (bounded by `PROVIDER_TIMEOUT_SECONDS`); a queue would let
   the UI poll and free the request thread, which matters once the Provider is a real third party
   instead of an in-process mock.

---

## Local-only references

Three files shaped this build but aren't in the repo — all gitignored, none are among BRIEF's
listed deliverables:

- **`BRIEF.md`** — the original assignment. Kept local as the source of truth for "what's actually
  required," cross-checked against at the end of every phase.
- **`GUIA-ARRANQUE.md`** — my own phase-by-phase execution plan, written before any code, that
  `CLAUDE.md`'s branch-per-phase workflow was built around.
- **`design_handoff_partner_onboarding/`** — a Claude-generated design reference (the "Industry"
  design system: CSS tokens + an HTML mockup) used to guide the frontend's visual styling. Not
  committed since visual polish is explicitly out of scope, but it's why the UI is more considered
  than a bare functional pass.

---

## AI usage

Claude Code was used throughout: options with trade-offs → choose and state why → implement →
adversarial review → reproduce bugs with a test before fixing them. Start at
[`AI_LOG.md`](./AI_LOG.md) — the curated index, caught-mistakes list, and reflection.
[`ai-log/`](./ai-log) has the full per-phase decision logs it links to:

| File | Phase |
|---|---|
| [`01-design.md`](./ai-log/01-design.md) | Schema, state machine, API contract |
| [`02-backend.md`](./ai-log/02-backend.md) | Endpoints, Provider client, transactions |
| [`03-frontend.md`](./ai-log/03-frontend.md) | Wizard, resume, validation states |
| [`04-tests.md`](./ai-log/04-tests.md) | Backend tests + e2e |
| [`prompts.md`](./ai-log/prompts.md) | Recurring review prompts used on backend code |
