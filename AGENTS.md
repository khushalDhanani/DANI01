# AIRIS Insights — Repository Agent Instructions

This is the shared instruction file for the AIRIS Insights monorepo.

These rules apply to all work in this repository. Before modifying code inside
`backend/` or `frontend/`, also read that folder's `AGENTS.md` because it contains
implementation-specific rules for that part of the system.

## Project Overview

AIRIS Insights is a database intelligence and data-quality platform built around
an existing Microsoft SQL Server database.

The application has two main parts:

- `backend/` — Python/FastAPI services for database discovery, profiling,
  analysis, data-quality evaluation, persistence, exports, and background work.
- `frontend/` — Expo / React Native / TypeScript application for web and native
  interfaces over the backend APIs.

The source MSSQL database contains a large production dataset and must be treated
as **read only**.

## Repository Structure

```text
/
├── AGENTS.md                  # Shared repository-wide rules
│
├── backend/
│   ├── AGENTS.md              # Backend-specific rules
│   ├── app/
│   │   ├── api/
│   │   ├── analysis/
│   │   ├── classification/
│   │   ├── core/
│   │   ├── db/
│   │   ├── discovery/
│   │   ├── modules/
│   │   ├── persistence/
│   │   ├── profiling/
│   │   ├── repositories/
│   │   ├── sampling/
│   │   ├── schemas/
│   │   └── workers/
│   ├── migrations/
│   └── tests/
│
└── frontend/
    ├── AGENTS.md              # Frontend-specific rules
    ├── app/                   # Expo Router route entry points
    ├── src/
    │   ├── api/
    │   ├── components/
    │   ├── constants/
    │   ├── features/
    │   ├── hooks/
    │   ├── lib/
    │   ├── providers/
    │   ├── schemas/
    │   ├── store/
    │   ├── types/
    │   └── utils/
    └── assets/
```

## Technology Overview

### Backend

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy / pyodbc
- Microsoft SQL Server
- Polars / NumPy
- PostgreSQL for AIRIS Insights internal persistence
- Alembic
- Celery / Redis where background processing is required
- pytest
- Ruff
- `uv` for Python dependency management

See [`backend/AGENTS.md`](backend/AGENTS.md) for backend architecture,
database-safety, testing, and SQL rules.

### Frontend

- Expo / React Native
- Expo Router
- TypeScript
- NativeWind / Tailwind
- TanStack Query
- Axios
- Zustand
- Zod

See [`frontend/AGENTS.md`](frontend/AGENTS.md) for frontend data-flow,
state-management, styling, responsiveness, typing, and Expo rules.

## Instruction Precedence

1. This root `AGENTS.md` applies everywhere.
2. When working in `backend/`, also follow `backend/AGENTS.md`.
3. When working in `frontend/`, also follow `frontend/AGENTS.md`.
4. More specific folder instructions override general guidance if there is a
   genuine conflict.

Never work from the root instructions alone when modifying backend or frontend
implementation details.

## Shared Engineering Rules

### 1. Inspect Before Editing

Read the existing implementation before changing it.

Verify:

- files and directories actually exist;
- existing exports, interfaces, functions, hooks, services, and components;
- current API contracts;
- nearby conventions and patterns;
- whether an existing module already solves the problem.

Do not invent files, APIs, database fields, exports, data, or architecture based
on assumptions.

### 2. Make Focused Changes

Keep changes limited to the requested problem.

Do not:

- reorganize unrelated working code;
- perform opportunistic refactors;
- rename unrelated files;
- rewrite working modules merely because another design is possible;
- introduce architectural changes without a concrete requirement.

Prefer the smallest reliable change that fits the existing architecture.

### 3. Reuse Existing Architecture

Extend existing modules and established patterns before creating parallel
abstractions.

Maintain separation of responsibilities between:

- route / transport layers;
- application and domain logic;
- data-access layers;
- API clients;
- state-management layers;
- presentation components.

Entry-point and route files should stay thin. Business logic belongs in the
appropriate domain/service/feature layer.

Refer to the nested `AGENTS.md` for the exact backend and frontend dependency
flow.

### 4. Preserve Backend/Frontend Contracts

The frontend and backend are one system.

When changing an API contract:

- update the backend request/response model;
- update the corresponding frontend TypeScript type;
- update the API module and consuming hooks/components where required;
- update affected tests;
- verify all consumers before considering the change complete.

Do not silently make the frontend compensate for an incorrect backend contract,
or the backend compensate for an incorrect frontend assumption.

Prefer fixing the contract at its source.

### 5. Source MSSQL Is Read Only

The existing source Microsoft SQL Server database is production data.

No feature on either side of the application may introduce source-database
mutation.

Do not design frontend actions, backend endpoints, scripts, migrations, tests,
or utilities that modify the source MSSQL database unless an explicit project
requirement changes this invariant.

Backend-specific SQL enforcement rules are defined in `backend/AGENTS.md`.

### 6. Treat Source Data as Sensitive

Assume database records may contain PII or other sensitive information.

Do not:

- expose raw sensitive values unnecessarily;
- log passwords, credentials, connection strings, or secrets;
- log large source-data payloads;
- add debugging output containing sensitive records;
- commit real credentials or `.env` files containing secrets.

Use environment configuration and the project's existing masking/privacy
utilities where appropriate.

### 7. Respect Data Scale

This system analyzes hundreds of database tables and potentially very large
datasets.

Never assume data is small.

Prefer:

- pagination;
- sampling;
- bounded queries;
- server-side counts/aggregations;
- virtualization where appropriate;
- explicit limits.

Avoid loading, transferring, or rendering entire large datasets when a bounded
operation can solve the problem.

Backend query rules and frontend rendering rules are defined in their respective
`AGENTS.md` files.

### 8. Keep Contracts and Types Explicit

Use explicit, typed data contracts.

Avoid loosely structured data when the shape is known.

Backend API models and frontend TypeScript interfaces must remain aligned.

Do not bypass the project's type-safety mechanisms to make an error disappear.
Fix the underlying contract or implementation instead.

### 9. Avoid Catch-All Code

Prefer small, focused modules with clear responsibilities.

Do not create generic dumping grounds such as oversized `utils` modules,
god-services, mega-components, or unrelated helper collections.

Place logic in the narrowest appropriate domain/module.

### 10. Dependencies Require Justification

Before adding a dependency:

1. Check whether the existing stack already provides the capability.
2. Confirm that the dependency is compatible with the affected runtime.
3. Prefer a small implementation with existing dependencies when reasonable.
4. Add a new framework, service, or infrastructure component only when there is
   a concrete requirement.

Do not introduce technology solely because it may be useful later.

### 11. Handle Errors Explicitly

Do not silently hide operational failures.

Errors should be handled at the correct layer and surfaced in a useful,
structured way.

Frontend data views must represent failure states appropriately.

Backend failures must be logged and handled according to the backend-specific
rules.

### 12. Tests and Validation Are Part of the Change

Changes are not complete merely because the edited code looks correct.

Run the checks appropriate to the modified side of the repository.

For backend commands and required tests, see `backend/AGENTS.md`.

For frontend type-checking, linting, Expo validation, and UI requirements, see
`frontend/AGENTS.md`.

Add or update tests for meaningful behavior changes and avoid regressions in
unrelated functionality.

## Repository-Wide Do / Don't Summary

### Do

- Inspect existing code before editing.
- Reuse existing modules and conventions.
- Keep changes narrow and task-focused.
- Respect frontend/backend boundaries.
- Keep API contracts synchronized.
- Preserve source-MSSQL read-only guarantees.
- Treat production data as sensitive.
- Design for large datasets.
- Keep types/contracts explicit.
- Run relevant validation before completion.
- Prefer simple, maintainable solutions.

### Don't

- Invent project structure or backend data.
- Refactor unrelated working code.
- Bypass established architectural layers.
- Mutate the source MSSQL database.
- Hard-code credentials, secrets, or environment-specific URLs.
- Log sensitive source records.
- Load or render unbounded datasets.
- Create catch-all utility modules or oversized components/services.
- Add dependencies or infrastructure without a clear requirement.
- Disable type, lint, safety, or validation rules merely to make code pass.
