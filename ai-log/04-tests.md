# Session 04 — Backend tests + e2e

> Most of the required backend coverage (state machine transitions, idempotency, all 4 Provider
> outcomes) was already built in Phase 2 (30 tests, see `02-backend.md`). This phase filled the
> two remaining gaps: the go-live rollback test, and the 2 canonical Playwright e2e tests.

---

### D18 — E2E test count: 3 files, not the stated "max 2" · _accepted, exception flagged_
`CLAUDE.md` caps e2e at 2 (happy path, reload-resumes); `invalid-routing.spec.ts` already existed as a 3rd, added earlier for the D13 product decision. Asked whether to fold it into one of the 2 or keep it separate and flag the exception — kept it separate. Not scope creep: it's a regression test for a specific decision, not general coverage padding.

### D19 — Go-live rollback test written despite `go_live` being a single atomic statement · _accepted_
`CLAUDE.md` asks for a "failure mid-transaction leaves no partial state" test; `go_live` is one `UPDATE`, so there's no multi-write sequence to fail partway through. Asked whether to skip and document that, or simulate a failure anyway (patch `commit()` to raise, assert the row stays at `VALIDATED`) — wrote it. Mostly proves SQLAlchemy's own rollback behaves correctly rather than bespoke logic, but it's cheap and directly matches the stated requirement.

---

## Verification evidence

- `test_go_live_failed_commit_leaves_no_partial_state`: monkeypatches `db.commit` to raise, confirms the session is still `VALIDATED` (not `LIVE`, not corrupted) after rollback. 37 backend tests total, all passing.
- 3 e2e specs, all passing against the real backend/Postgres: `happy-path.spec.ts` (full flow to Live), `resume-on-reload.spec.ts` (reload at `DETAILS_OK`, `VALIDATED`, and `LIVE`, each time confirming the correct screen and data), `invalid-routing.spec.ts` (existing, D13).

## Bugs/gaps caught while writing these, not by reading the code

- **Playwright ran all 3 spec files in parallel by default**, each resetting and racing the same single hardcoded-partner session — two tests failed with flaky-looking "element not found" errors that were actually a config problem, not a test or app bug. `fullyParallel: false` only stops parallelism *within* a file; `workers: 1` is what actually forces every file to run serially.
- **`ValidateStep`'s read-only company/account fields had no `htmlFor`/`id` label association**, unlike `DetailsStep`'s real form fields — inconsistent, and it broke `getByLabel()` in the resume test. Fixed by adding matching `id`/`htmlFor` pairs rather than working around it with a looser selector in the test.
- **A bare `npm install` fails on any machine other than this one.** `openapi-typescript@7.13.0`'s peer range (`typescript@^5.x`) predates the project's TypeScript 6 pin — `node_modules` here only worked because it was never fully re-resolved since an early install. Caught by simulating a fresh machine: copied the working tree (respecting `.gitignore`, so `BRIEF.md`/`GUIA-ARRANQUE.md` were correctly absent, matching a real clone) into an isolated directory, then ran the README's exact commands against fresh databases and a fresh `node_modules`/venv. `npm install` failed with `ERESOLVE`; confirmed it wasn't a fluke by re-running `npm install --dry-run` in the real project dir too — same failure. Fixed with `frontend/.npmrc` (`legacy-peer-deps=true`); TS6 already worked fine in practice (`tsc -b` was clean throughout), the peer range was just stale metadata. Also fixed a real doc bug found the same way: the README's `DATABASE_URL` example was missing the `+psycopg` driver suffix that `.env.example`/`config.py` actually default to.
