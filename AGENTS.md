# AIRIS Insights — Repository Agent Instructions

This is the shared instruction entry point for the AIRIS Insights monorepo.

These rules apply everywhere. Before modifying code inside `backend/` or
`frontend/`, also read that folder's `AGENTS.md`.

## Project Overview

AIRIS Insights is a database intelligence and data-quality platform for safely
discovering, profiling, classifying, and analyzing an existing Microsoft SQL
Server database.

The repository contains:

- `backend/` — Python/FastAPI analysis API, MSSQL discovery/profiling,
  data-quality logic, persistence, exports, and background jobs.
- `frontend/` — Expo/React Native/TypeScript application for web and native
  interfaces over the backend APIs.

The source MSSQL database is production data and is always **READ ONLY**.

## Repository Structure

```text
/
├── AGENTS.md
├── README.md
├── backend/
│   ├── AGENTS.md
│   ├── README.md
│   ├── app/
│   │   ├── analysis/
│   │   ├── api/
│   │   ├── classification/
│   │   ├── core/
│   │   ├── db/
│   │   ├── discovery/
│   │   ├── models/
│   │   ├── modules/
│   │   ├── persistence/
│   │   ├── profiling/
│   │   ├── repositories/
│   │   ├── sampling/
│   │   ├── schemas/
│   │   └── workers/
│   ├── migrations/
│   └── tests/
└── frontend/
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── README.md
    ├── app/
    └── src/
```

This tree is a guide, not a substitute for inspecting the filesystem. Never
invent a file, route, export, schema, table, field, or component because a
document implies it exists.

## Instruction Precedence

1. This root `AGENTS.md` applies repository-wide.
2. `backend/AGENTS.md` applies to backend work.
3. `frontend/AGENTS.md` applies to frontend work.
4. A more specific nested instruction may refine a general rule.
5. If documentation and code disagree about current structure or versions,
   inspect the code/configuration and treat executable configuration as the
   source of truth.

## Shared Engineering Rules

### 1. Inspect Before Editing

Before changing code:

- read the existing implementation;
- locate all consumers of the behavior being changed;
- verify current types, schemas, routes, hooks, services, and exports;
- search for an existing abstraction before creating another one;
- inspect nearby tests;
- inspect configuration rather than duplicating constants.

Do not implement from assumptions.

### 2. Keep Changes Focused

Prefer the smallest reliable change that fits the existing architecture.

Do not:

- refactor unrelated working code;
- rename unrelated files;
- reorganize directories without a concrete need;
- introduce speculative abstractions;
- add infrastructure because it may be useful later.

### 3. Preserve Layer Boundaries

Keep responsibilities separated.

Typical flow:

```text
Frontend route/view
    ↓
Frontend query hook
    ↓
Frontend API module
    ↓
FastAPI route
    ↓
Service / analysis / domain logic
    ↓
Repository / discovery / DB layer
```

Route and entry-point files should remain thin. Business logic belongs in the
appropriate service/domain/feature layer.

### 4. Backend and Frontend Contracts Must Stay Synchronized

An API contract change is a cross-layer change.

When request/response behavior changes, inspect and update as required:

- backend Pydantic schemas;
- backend routes/services;
- frontend TypeScript request/response types;
- frontend API modules;
- TanStack Query hooks;
- consuming screens/components;
- tests and exports.

Do not make one side silently compensate for a broken or outdated contract on
the other side. Fix the contract at its source.

### 5. Source MSSQL Is Read Only

Never introduce a source-database mutation path.

Forbidden against the source MSSQL database include:

- `INSERT`
- `UPDATE`
- `DELETE`
- `MERGE`
- `TRUNCATE`
- `ALTER`
- `DROP`
- `CREATE`

Do not add frontend actions, API endpoints, scripts, migrations, jobs, or tests
that mutate source MSSQL.

AIRIS internal persistence is separate and may be writable.

### 6. Treat Source Data as Sensitive

Assume source rows can contain PII or other sensitive information.

Do not:

- commit secrets or populated `.env` files;
- log passwords or credentials;
- log connection strings containing passwords;
- dump large source records to logs;
- expose raw PII when a summary/masked value is sufficient;
- add debugging output containing sensitive production values.

### 7. Design for Large Data

Never assume the database, table, API result, or UI list is small.

Prefer:

- metadata queries;
- bounded queries;
- configurable sampling;
- pagination;
- server-side aggregation;
- limited concurrency;
- virtualization for large UI lists;
- transferring only the data required for the operation.

Never compute authoritative totals from a partial page.

### 8. Keep Business Definitions Centralized

Data-quality and integrity rules are domain contracts.

For each business rule or issue type—such as qualifying email, missing phone,
duplicate identity, active/deleted status, invalid contact, or severity—there
must be one canonical backend definition.

The following must not independently reimplement the same rule:

- dashboard KPIs;
- summary counts;
- drill-down totals;
- drill-down item queries;
- CSV/Excel exports;
- background analysis;
- frontend displays.

If multiple surfaces answer the same business question, they must reuse the same
predicate/service/domain definition.

### 9. Count, List, Summary, and Export Must Agree

For a paginated issue or quality endpoint:

- the `total` query and item query must use the same qualification logic;
- joins and active/deleted filters must remain consistent;
- exports must reuse the same business predicate as the API/UI;
- a frontend must not derive the total from the current page;
- issue codes and severity semantics must not be reinterpreted independently by
  different screens.

A mismatch between KPI, drill-down, and export is a correctness bug.

### 10. Keep Types and Contracts Explicit

Use typed, explicit models whenever the structure is known.

Do not weaken type/lint rules or return arbitrary untyped structures merely to
make code pass.

### 11. Dependencies Require Justification

Before adding a dependency:

1. Check whether the existing stack already solves the problem.
2. Confirm compatibility with the affected runtime.
3. Prefer existing project patterns when reasonable.
4. Add new infrastructure/frameworks only for a concrete requirement.

### 12. Errors Must Be Visible

Do not silently swallow failures.

Handle errors at the correct layer and surface useful structured error states.
Avoid broad `except Exception: pass` behavior and equivalent frontend failure
suppression.

### 13. Configuration Is a Source of Truth

Do not copy tunable runtime values into business logic or documentation when
they already exist in configuration.

When a new environment-backed setting is added, update the relevant
`.env.example` in the same change unless there is a documented reason not to.

### 14. Validate the Whole Change

A change is not complete because one edited file looks correct.

Run the relevant backend/frontend validation from the nested `AGENTS.md` files.
For cross-layer changes, validate both sides.

### 15. Automated CI Quality Gate & Branch Protection

All Pull Requests and commits to `main` are automatically verified by GitHub Actions ([`.github/workflows/quality.yml`](.github/workflows/quality.yml)):

- **Backend Gate**: `uv run ruff check .` + `uv run ruff format --check .` + `uv run pytest -m "not integration"` (with **80% minimum branch coverage gate**).
- **Frontend Gate**: `npm run typecheck` + `npm run lint` (`--max-warnings=0`) + `npm test` (Jest under `__tests__/`) + `npm run build:web`.

Both jobs must pass for a PR to be mergeable. Live MSSQL integration tests are marked with `@pytest.mark.integration` and run separately on demand.

## Repository-Wide Do / Don't

### Do

- inspect first;
- reuse existing architecture;
- keep changes narrow;
- centralize business rules;
- synchronize API contracts;
- design for large datasets;
- protect source MSSQL;
- protect sensitive data;
- run relevant validation.

### Don't

- invent project structure or data;
- duplicate data-quality predicates;
- mutate source MSSQL;
- compute totals from partial pages;
- hard-code secrets or backend URLs;
- add unexplained dependencies;
- bypass type/lint/safety rules;
- hide errors;
- refactor unrelated code.

## Folder-Specific Instructions

- [Backend instructions](backend/AGENTS.md)
- [Frontend instructions](frontend/AGENTS.md)
