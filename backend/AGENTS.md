# AIRIS Insights — Backend Agent Instructions

These rules apply to `backend/`.

Read the repository root [`AGENTS.md`](../AGENTS.md) first. This file contains
backend-specific requirements.

## Backend Scope

The backend is a Python 3.12+ FastAPI application that safely analyzes an
existing production Microsoft SQL Server database.

The backend also owns AIRIS's internal persistence, analysis orchestration,
exports, and Celery background work.

## Source of Truth

Before editing:

- inspect the filesystem and existing implementation;
- treat `pyproject.toml` / `uv.lock` as dependency sources of truth;
- treat `app/core/config.py` as the source of truth for runtime defaults;
- treat FastAPI/Pydantic models and actual routes as the API contract;
- do not preserve stale documentation assumptions over working code.

The application entry point is `app.main:app`.

Do not add production application behavior to the legacy root `main.py` unless
the project intentionally changes its entry-point strategy.

## Current Backend Structure

```text
backend/
├── app/
│   ├── analysis/
│   ├── api/
│   │   └── routes/
│   ├── classification/
│   ├── core/
│   ├── db/
│   ├── discovery/
│   ├── models/
│   ├── modules/
│   │   ├── definitions/
│   │   └── person/
│   ├── persistence/
│   ├── profiling/
│   ├── repositories/
│   ├── sampling/
│   ├── schemas/
│   ├── workers/
│   └── main.py
├── migrations/
├── tests/
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

This is descriptive, not permission to invent missing modules. Verify the
filesystem before creating or referencing anything.

# 1. Non-Negotiable MSSQL Read-Only Rule

The source Microsoft SQL Server database is production data.

**Never modify it.**

Do not execute source MSSQL statements containing mutation/DDL operations such
as:

- `INSERT`
- `UPDATE`
- `DELETE`
- `MERGE`
- `TRUNCATE`
- `ALTER`
- `DROP`
- `CREATE`

Do not create temporary/business tables in the source database.

Do not execute stored procedures unless they have been explicitly verified to
be read-only.

All source MSSQL access must go through the project's read-only execution path
and safety guard.

Use least-privilege/read-only MSSQL credentials whenever possible. Application
guards are a second safety layer, not a replacement for database permissions.

## Values Must Be Parameterized

Never interpolate user/data values directly into SQL strings.

Use SQLAlchemy/text parameters for values.

## Identifiers Require Separate Validation

SQL identifiers such as schema, table, and column names cannot be treated like
normal bind values.

When dynamic identifiers are necessary:

- obtain them from trusted discovery metadata or a validated allowlist;
- validate them before interpolation;
- schema-qualify objects where appropriate;
- quote identifiers safely for SQL Server;
- never insert arbitrary client-provided identifier text directly into SQL.

# 2. Source MSSQL vs AIRIS Internal Persistence

These are separate systems.

### Source MSSQL

- production data;
- read-only;
- discovery/profiling/analysis source.

### AIRIS Persistence

- SQLite by default for local development;
- PostgreSQL in Docker/production-style setups;
- stores AIRIS-owned state/results.

Alembic migrations may modify **only AIRIS internal persistence**.

Never point Alembic migrations, schema creation, or destructive migration
operations at the production source MSSQL database.

# 3. Backend Architecture

## `api/`

FastAPI transport layer only.

Responsible for:

- request parsing;
- validation;
- dependency resolution;
- calling application/domain services;
- mapping expected exceptions;
- returning typed responses.

Do not place SQL or substantial business analysis logic in route functions.

## `core/`

Application-wide infrastructure:

- settings;
- logging;
- exceptions;
- constants/lifecycle.

Use `pydantic-settings` for environment-backed configuration.

## `db/`

Database connectivity and low-level execution.

`db/mssql.py` owns MSSQL connectivity/read-only execution concerns.

Do not place domain-quality rules in DB connection modules.

Internal persistence connection/session management belongs in the internal DB
layer.

## `discovery/`

Database structure discovery:

- schemas;
- tables;
- columns;
- primary/foreign keys;
- indexes;
- estimated counts;
- relationships.

Prefer SQL Server catalog/system metadata over expensive data scans.

## `sampling/`

Bounded sampling strategies.

Sampling sizes and thresholds must come from configuration, not duplicated
magic numbers.

## `profiling/`

Column/table profiling and statistics.

Use SQL Server for efficient simple aggregates where appropriate and Polars for
bounded Python-side profiling.

Never automatically load an entire large table into Python.

## `classification/`

Semantic/data classification logic.

Keep classification rules deterministic and testable. Do not mix them into API
routes or UI-oriented formatting.

## `analysis/`

Coordinates analysis workflows.

Analysis/domain code must not depend on FastAPI transport details.

Keep background execution adapters separate from core analysis behavior so the
same logic can be invoked and tested without Celery.

## `repositories/`

Data-access boundary for reusable source/internal DB queries where appropriate.

Do not duplicate the same domain query across unrelated services.

## `modules/`

Domain-specific analysis modules.

A module should own its domain rules and expose reusable services/predicates
rather than duplicating SQL in routes, summaries, and exports.

## `persistence/` / `models/`

AIRIS-owned persistence and data models.

Keep source MSSQL models/concepts separate from AIRIS internal result storage.

## `workers/`

Celery/background execution adapters.

Workers should call reusable analysis/services; they should not become a second
copy of business logic.

# 4. Canonical Data-Quality Rules

This is a critical project invariant.

Each data-quality/business definition must have **one canonical backend
implementation**.

Examples:

- qualifying email;
- missing email;
- qualifying phone;
- invalid contact;
- duplicate identity/contact;
- active/deleted person;
- issue severity;
- issue code/meaning.

Do not independently rewrite a qualifying predicate for:

- dashboard summary KPIs;
- issue count endpoints;
- issue drill-down item queries;
- analysis results;
- CSV export;
- Excel export;
- summary export;
- worker tasks.

Prefer a shared service, reusable SQL fragment/builder, domain predicate, or
repository method appropriate to the architecture.

A change to the definition must update one source of truth and all consumers
must inherit the new behavior.

# 5. Count / List / Export Consistency

For every paginated issue endpoint:

- `total` and `items` must use the same qualification predicate;
- all required joins must be equivalent;
- active/deleted filters must be equivalent;
- null/empty normalization must be equivalent;
- export rows must use the same qualification definition;
- summary KPIs must represent the same business meaning.

Never:

- derive total from `len(current_page)`;
- use a looser predicate for export;
- use a stricter predicate for the dashboard;
- copy/paste similar SQL and assume it will remain synchronized.

Add regression tests whenever a bug is caused by count/list/export divergence.

# 6. Data Scale & MSSQL Performance

The production database is large. Never assume a table is small.

Before expensive work, prefer to know:

- estimated row count;
- column count;
- indexes/primary key;
- table size when practical.

Do not run unrestricted:

```sql
SELECT *
FROM SomeLargeTable;
```

Use a controlled bound or configured sampling strategy.

## Runtime Limits

`app/core/config.py` is the source of truth for:

- MSSQL pool size;
- MSSQL max overflow;
- query timeout;
- profile sample limits;
- analysis sample sizes;
- table-size thresholds;
- maximum concurrent table analysis;
- Celery timeout/concurrency.

Do not duplicate these values as hard-coded constants in services or docs.

Minimize data transferred from MSSQL into Python.

# 7. Celery / Background Jobs

Celery and Redis are active backend infrastructure.

Background tasks must:

- call reusable application/domain logic;
- honor configured task time limits;
- honor configured worker/concurrency limits;
- avoid unbounded MSSQL fan-out;
- be retry/idempotency-aware where retries are possible;
- not leave AIRIS internal analysis state inconsistent after failure;
- never weaken source MSSQL read-only protections.

Do not increase worker concurrency merely to make analysis appear faster without
considering source DB load.

# 8. Configuration

Configuration belongs in environment variables and Pydantic Settings.

Never hard-code secrets.

When adding or renaming an environment-backed setting:

1. update `app/core/config.py`;
2. update `backend/.env.example`;
3. update Docker/Compose environment wiring if applicable;
4. update documentation if developers must configure it;
5. update tests for meaningful behavior.

Do not commit populated `.env` files.

# 9. API Conventions

Use versioned routes under:

```text
/api/v1/...
```

Current top-level areas are registered for:

- health;
- database;
- analysis;
- analysis runs;
- domain modules.

Use Pydantic models for stable request/response contracts.

Routes call services/domain code; they do not perform analysis directly.

When changing a response shape, remember the root cross-layer rule: inspect and
update frontend types and consumers in the same change when necessary.

# 10. Errors

Do not silently swallow failures.

Avoid:

```python
try:
    ...
except Exception:
    pass
```

Use project exceptions where appropriate and preserve actionable context.

One table failing during a multi-table analysis should be isolated when the
workflow can safely continue, but the failure must still be visible in status,
logs, or result metadata.

Do not expose secrets or raw sensitive database values in client-facing error
messages.

# 11. Logging

Use structured/useful logging context where applicable, such as:

- request ID;
- analysis run ID;
- database/schema/table;
- operation;
- duration;
- row/sample count.

Never log:

- passwords;
- secrets;
- credential-bearing connection strings;
- large source payloads;
- unnecessary PII.

Do not log full destructive-query text if doing so could leak sensitive values;
log enough context to diagnose the blocked operation safely.

# 12. Python Standards

Use:

- type hints;
- small focused functions/classes;
- descriptive names;
- Pydantic models for API contracts;
- dependency injection where it improves testability;
- parameterized SQL;
- async only where it provides real value.

Avoid:

- giant service classes;
- global mutable state;
- generic dumping-ground `utils.py`;
- duplicated SQL;
- hidden side effects;
- business logic in routes;
- arbitrary dicts when a known typed structure is appropriate.

# 13. Exports

CSV/Excel exports are another representation of domain results, not a separate
business-rule implementation.

Exports must:

- reuse the same qualification logic as API/UI results;
- respect sensitive-data requirements;
- use bounded/streaming/chunked strategies when result size is large;
- avoid loading unnecessarily large result sets into memory;
- preserve stable column meanings.

# 14. Testing

Use `pytest`.

All test/experimental test files belong under `backend/tests/`. Do not create
one-off `test_*.py` files at backend root.

Tests should cover affected behavior, especially:

- configuration;
- read-only SQL protection;
- MSSQL connection/error handling;
- discovery;
- sampling;
- profiling/classification;
- API contracts;
- analysis orchestration;
- data-quality predicates;
- KPI/count/list/export consistency;
- background-job behavior where relevant.

Critical safety tests must prove mutation SQL is rejected.

Never run destructive tests against production MSSQL.

Use mocks/fixtures or an explicitly safe test database for tests that require DB
behavior.

# 15. Development Commands

Install:

```bash
uv sync
```

Run API:

```bash
uv run uvicorn app.main:app --reload
```

Tests:

```bash
uv run pytest
```

Lint:

```bash
uv run ruff check .
```

Formatting check:

```bash
uv run ruff format --check .
```

Format:

```bash
uv run ruff format .
```

# 16. Backend Definition of Done

A backend change is complete only when relevant items below are satisfied:

- [ ] source MSSQL read-only guarantees are preserved;
- [ ] no unbounded query/table scan was introduced;
- [ ] runtime limits come from configuration where applicable;
- [ ] data-quality rules have one canonical implementation;
- [ ] KPI/count/list/export paths remain consistent;
- [ ] request/response contracts are typed;
- [ ] `.env.example` is synchronized for new settings;
- [ ] migrations target only AIRIS internal persistence;
- [ ] affected tests pass;
- [ ] `uv run ruff check .` passes;
- [ ] formatting is valid;
- [ ] frontend consumers were updated if the API contract changed;
- [ ] no secrets or unnecessary PII are logged/exposed.
