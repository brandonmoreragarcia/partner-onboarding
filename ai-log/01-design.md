# Session 01 — Design: schema, state machine, API contract

---

### D1 — Backend stack: Python instead of Node · _redirected_
Brief prefers Node/TS; chose Python + FastAPI instead — most comfortable stack from recent work experience.

### D2 — Provider items: separate `items` table vs JSONB on `sessions` · _accepted_
Chose the separate table with an FK over JSONB — better normalization, room for future queries/indexes on items.

### D3 — Session identity: `UNIQUE` constraint on `partner_id` · _accepted_
Chose the DB-level `UNIQUE` + atomic upsert over query-for-latest — enforces integrity at the DB level, no race window creating duplicate sessions.

### D4 — Concurrent `POST /validate` returns `200`, not `409` · _accepted_
A duplicate in-flight validate returns the current state instead of erroring — better UX, and avoids racing two simultaneous validation attempts.

### D5 — `status` column: `TEXT` + `CHECK` over native Postgres `ENUM` · _accepted_
Chose `VARCHAR` + `CHECK` (`SQLAlchemy Enum(native_enum=False)`) — same DB-level safety as a native enum, without the painful migration story when the value list changes.

### D6 — `validation_log`: insert-only audit table · _redirected_
Initially recommended "latest result only"; pushed back for audit/debugging value, landed on an insert-only log table — good balance of cost vs. usefulness.

### D7 — `models.py`/`schemas.py`: entity-per-file split · _accepted_
Chose one file per table (7 files) over an aggregate-boundary split (5 files) — discoverability mattered more than fewer files, especially since `state_machine.py` imports heavily from both.

