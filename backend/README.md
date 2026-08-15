# AIRIS Insights

AIRIS Insights is a read-only database intelligence and data-quality platform
for exploring, profiling, classifying, and analyzing an existing Microsoft SQL
Server database.

It combines a **FastAPI/Python backend** with an **Expo/React Native/TypeScript
frontend** and keeps AIRIS's own persistence separate from the production MSSQL
source.

> **Source MSSQL is READ ONLY.** AIRIS must never mutate the production source
> database.

## Core Capabilities

- MSSQL connectivity and health checks
- schema/table/column/key/index discovery
- safe table sampling
- table and column profiling
- semantic classification
- analysis orchestration and persisted analysis runs
- domain/data-quality modules
- issue summaries, drill-downs, and exports
- responsive web/native dashboards and database explorer
- Celery/Redis background processing

## Architecture

```text
Expo / React Native
Routes → Feature Views → Query Hooks → API Modules
                         │
                         ▼
                    FastAPI /api/v1
Routes → Services / Analysis / Domain Logic → Repositories
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
      MSSQL Source             AIRIS Persistence
       READ ONLY              SQLite / PostgreSQL
                                      │
                                      ▼
                                 Redis / Celery
```

## Repository Structure

```text
DANI01/
├── AGENTS.md
├── README.md
├── backend/
│   ├── AGENTS.md
│   ├── README.md
│   ├── app/
│   ├── migrations/
│   ├── tests/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
└── frontend/
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── README.md
    ├── app/
    ├── src/
    ├── package.json
    └── package-lock.json
```

## Tech Stack

### Backend

- Python 3.12+
- FastAPI
- Pydantic / pydantic-settings
- SQLAlchemy
- pyodbc + Microsoft ODBC Driver 18
- Polars / NumPy
- SQLite for default local AIRIS persistence
- PostgreSQL for Docker/production-style AIRIS persistence
- Alembic
- Celery / Redis
- openpyxl
- pytest / Ruff
- `uv`

### Frontend

- Expo 57
- React 19 / React Native
- Expo Router
- TypeScript
- NativeWind / Tailwind CSS
- TanStack Query
- Axios
- Zustand
- Zod
- React Hook Form
- Lucide React Native

Exact dependency versions are defined by `backend/pyproject.toml`,
`backend/uv.lock`, `frontend/package.json`, and `frontend/package-lock.json`.

# Quick Start

## Prerequisites

- Git
- Python 3.12+
- `uv`
- Node.js + npm
- Microsoft ODBC Driver 18 for SQL Server
- network access and read-only credentials for the target MSSQL database
- Docker if using the full backend stack

## 1. Clone

```bash
git clone https://github.com/khushalDhanani/DANI01.git
cd DANI01
```

## 2. Backend

```bash
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload
```

Configure MSSQL values in `backend/.env`:

```env
MSSQL_HOST=
MSSQL_PORT=1433
MSSQL_DATABASE=
MSSQL_USERNAME=
MSSQL_PASSWORD=
MSSQL_DRIVER="ODBC Driver 18 for SQL Server"
```

The backend defaults to SQLite for AIRIS's local internal persistence:

```text
sqlite:///./dbinsights.db
```

The API runs at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

### Docker backend stack

From `backend/`:

```bash
docker compose up --build
```

The compose stack includes:

- PostgreSQL
- Redis
- FastAPI
- Celery worker

Stop it with:

```bash
docker compose down
```

Use `docker compose down -v` only when you intentionally want to remove the
local AIRIS PostgreSQL development volume.

## 3. Frontend

In another terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run start
```

Web / iOS simulator:

```env
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Android emulator:

```env
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000/api/v1
```

Physical device on the same LAN:

```env
EXPO_PUBLIC_API_URL=http://<YOUR_LAN_IP>:8000/api/v1
```

Specific targets:

```bash
npm run web
npm run android
npm run ios
```

# API

The application API is versioned under:

```text
/api/v1
```

Top-level route areas currently include:

- `/api/v1/health`
- `/api/v1/database`
- `/api/v1/analysis`
- `/api/v1/analysis-runs`
- domain/module routes under `/api/v1/...`

Use `/docs` as the source of truth for the exact current endpoint contracts.

# Development Validation

## Backend

```bash
cd backend
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Frontend

```bash
cd frontend
npm run typecheck
npm run lint
npm run build:web
```

`npm run build:web` is especially important when a change affects routing,
bundling, shared configuration, or web rendering.

# Data Safety

## Source MSSQL

Forbidden against source MSSQL:

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

Use read-only database credentials whenever possible in addition to application
guards.

For large datasets:

- prefer catalog/metadata queries;
- use bounded queries and configured sampling;
- paginate list endpoints;
- limit MSSQL concurrency;
- avoid unrestricted full-table reads;
- transfer only necessary data into Python.

## Data-Quality Consistency

A business/data-quality definition must have one canonical backend
implementation.

Dashboard KPI, total count, paginated drill-down, CSV export, Excel export, and
other summaries must not implement slightly different versions of the same
predicate.

If those surfaces disagree, treat it as a correctness defect.

# Engineering Instructions

Read [AGENTS.md](AGENTS.md) before modifying the repository.

Then read the relevant nested file:

- [backend/AGENTS.md](backend/AGENTS.md)
- [frontend/AGENTS.md](frontend/AGENTS.md)

# Subproject Documentation

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
