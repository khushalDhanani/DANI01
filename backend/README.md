# AIRIS Insights Backend

FastAPI backend for AIRIS Insights.

The backend safely discovers, samples, profiles, classifies, and analyzes an
existing Microsoft SQL Server database while storing AIRIS-owned analysis state
separately.

> **The source MSSQL database is READ ONLY.**

## Stack

- Python 3.12+
- FastAPI
- Pydantic / pydantic-settings
- SQLAlchemy
- pyodbc
- Microsoft ODBC Driver 18
- Polars / NumPy
- SQLite / PostgreSQL for AIRIS internal persistence
- Alembic
- Celery / Redis
- openpyxl
- pytest / Ruff
- `uv`

Exact versions are defined in `pyproject.toml` and `uv.lock`.

## Structure

```text
backend/
├── app/
│   ├── analysis/
│   ├── api/routes/
│   ├── classification/
│   ├── core/
│   ├── db/
│   ├── discovery/
│   ├── models/
│   ├── modules/
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
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

The FastAPI entry point is:

```text
app.main:app
```

## Local Setup

```bash
cp .env.example .env
uv sync
```

Configure source MSSQL access in `.env`:

```env
APP_NAME="AIRIS Insights"
APP_ENV=development
APP_DEBUG=true

MSSQL_HOST=
MSSQL_PORT=1433
MSSQL_DATABASE=
MSSQL_USERNAME=
MSSQL_PASSWORD=
MSSQL_DRIVER="ODBC Driver 18 for SQL Server"

MSSQL_POOL_SIZE=5
MSSQL_MAX_OVERFLOW=2
MSSQL_QUERY_TIMEOUT=30
```

Use a read-only SQL Server login whenever possible.

### AIRIS Internal Persistence

Local configuration defaults to SQLite:

```env
POSTGRES_URL=sqlite:///./dbinsights.db
```

Docker overrides this with PostgreSQL.

### Redis / Celery

Default local Redis URL:

```env
REDIS_URL=redis://localhost:6379/0
```

Runtime defaults for Celery, sampling, analysis thresholds, and concurrency are
defined in `app/core/config.py`.

When adding environment-backed settings, keep `.env.example` synchronized.

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

OpenAPI:

```text
http://localhost:8000/openapi.json
```

## Docker

The backend Compose stack includes PostgreSQL, Redis, FastAPI, and a Celery
worker.

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

Remove local PostgreSQL development data too:

```bash
docker compose down -v
```

This removes AIRIS's Docker persistence volume; it does not modify source MSSQL.

## API Areas

The application registers versioned routes under `/api/v1`, including:

- `/api/v1/health`
- `/api/v1/database`
- `/api/v1/analysis`
- `/api/v1/analysis-runs`
- domain/module routes under `/api/v1/...`

Use `/docs` for exact current endpoints.

## Database Responsibilities

### Source MSSQL

Used for discovery/profiling/analysis only.

Never execute:

```text
INSERT
UPDATE
DELETE
MERGE
TRUNCATE
ALTER
DROP
CREATE
```

Use parameterized query values and validated/quoted dynamic identifiers.

### AIRIS Internal Database

SQLite/PostgreSQL stores AIRIS-owned state and results.

Alembic migrations apply only to this internal persistence layer.

## Data-Quality Consistency

One business definition must power every representation of the same issue.

For example, a `MISSING_EMAIL` definition should not be separately implemented
for:

- dashboard count;
- issue total;
- paginated rows;
- CSV export;
- Excel export.

Reuse a canonical service/predicate/query definition. Count and item queries must
use equivalent joins and filters.

## Large-Database Rules

- inspect metadata before expensive analysis;
- use bounded queries;
- use configured sample sizes;
- minimize transferred rows/columns;
- limit MSSQL concurrency;
- prefer SQL Server for simple aggregates;
- use Polars for bounded Python-side profiling;
- never load an entire large table into Python by default.

`app/core/config.py` is the source of truth for sample sizes, table thresholds,
pool settings, analysis concurrency, and Celery limits.

## Background Jobs

Celery uses Redis for broker/result backend.

Workers must call reusable application logic and preserve all read-only MSSQL
guards.

Do not increase worker concurrency without considering MSSQL production load.

## Development Commands

```bash
uv sync
uv run uvicorn app.main:app --reload
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Agent Instructions

Read:

1. [`../AGENTS.md`](../AGENTS.md)
2. [`AGENTS.md`](AGENTS.md)

before changing backend code.
