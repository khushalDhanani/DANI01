# AIRIS Insights

**AIRIS Insights** is a read-only database intelligence and data-quality platform for exploring, profiling, classifying, and analyzing large Microsoft SQL Server databases.

It combines a **FastAPI backend** with an **Expo / React Native frontend** and is designed to analyze production MSSQL data safely without modifying the source database.

> [!IMPORTANT]
> The source Microsoft SQL Server database is **READ ONLY**. Source-data mutation (`INSERT`, `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE`, `ALTER`, `DROP`, `CREATE`, etc.) is not allowed.

## Core Capabilities

* MSSQL connection and health checks
* Schema, table, column, key, index, and relationship discovery
* Safe, bounded sampling for large tables
* Table and column profiling
* Null, empty, distinct, range, length, and common-value analysis
* Semantic/data classification
* Analysis orchestration and run persistence
* Domain-specific analysis modules
* Data-quality dashboards and issue views
* Database/table explorer
* Responsive web, iOS, and Android frontend

## Architecture

```text
┌───────────────────────────────────────────────────────────┐
│                 Expo / React Native                       │
│ Routes → Feature Views → Query Hooks → API Modules        │
└───────────────────────────┬───────────────────────────────┘
                            │ HTTP / JSON
                            ▼
┌───────────────────────────────────────────────────────────┐
│                       FastAPI                             │
│ API Routes → Analysis / Services → Repositories           │
└───────────────────┬───────────────────────┬───────────────┘
                    │                       │
                    ▼                       ▼
        Microsoft SQL Server       SQLite / PostgreSQL
        Production Source          AIRIS Internal Data
             READ ONLY
                                            │
                                            ▼
                                      Redis / Celery
                                      Background Jobs
```

AIRIS separates the production source database from its own internal persistence:

| Database             | Purpose                                 | Write Access       |
| -------------------- | --------------------------------------- | ------------------ |
| Microsoft SQL Server | Existing production data being analyzed | **No — read only** |
| SQLite / PostgreSQL  | AIRIS analysis state/results            | Yes                |

Local backend development defaults to SQLite for AIRIS internal persistence. Docker-based development uses PostgreSQL.

## Repository Structure

```text
DANI01/
├── AGENTS.md                  # Shared engineering/agent rules
├── README.md
│
├── backend/
│   ├── AGENTS.md              # Backend-specific rules
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
│   ├── tests/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
│
└── frontend/
    ├── AGENTS.md              # Frontend-specific rules
    ├── app/                   # Expo Router entries
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
    ├── app.json
    ├── package.json
    └── tsconfig.json
```

## Tech Stack

### Backend

* Python 3.12+
* FastAPI
* Pydantic v2 / pydantic-settings
* SQLAlchemy 2.x
* pyodbc + Microsoft ODBC Driver 18
* Polars / NumPy
* SQLite (default local internal persistence)
* PostgreSQL
* Alembic
* Celery / Redis
* pytest / Ruff
* `uv`
* Docker / Docker Compose

### Frontend

* Expo 57
* React 19 / React Native
* Expo Router
* TypeScript
* NativeWind / Tailwind CSS
* TanStack Query
* Axios
* Zustand
* Zod
* React Hook Form
* Lucide React Native

# Getting Started

## Prerequisites

Install:

* Git
* Python 3.12+
* [`uv`](https://docs.astral.sh/uv/)
* Node.js + npm
* Microsoft ODBC Driver 18 for SQL Server
* Access to the target SQL Server
* Docker, if using the full backend stack

Redis is also required when running Celery/background jobs outside Docker.

## 1. Clone

```bash
git clone https://github.com/khushalDhanani/DANI01.git
cd DANI01
```

# Backend

## 2. Configure

```bash
cd backend
cp .env.example .env
```

Set the MSSQL connection:

```env
APP_NAME="AIRIS Insights"
APP_ENV=development
APP_DEBUG=true

MSSQL_HOST=your-sql-server-host
MSSQL_PORT=1433
MSSQL_DATABASE=your-database
MSSQL_USERNAME=your-username
MSSQL_PASSWORD=your-password
MSSQL_DRIVER="ODBC Driver 18 for SQL Server"

MSSQL_POOL_SIZE=5
MSSQL_MAX_OVERFLOW=2
MSSQL_QUERY_TIMEOUT=30
```

Never commit real credentials or the populated `.env`.

The backend defaults to these internal services for local development:

```env
POSTGRES_URL=sqlite:///./dbinsights.db
REDIS_URL=redis://localhost:6379/0
```

Despite the variable name `POSTGRES_URL`, the local default is SQLite.

## 3. Install

```bash
uv sync
```

## 4. Run

```bash
uv run uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger/OpenAPI UI:

```text
http://localhost:8000/docs
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

## Docker Backend

The included Compose stack runs:

* PostgreSQL
* Redis
* FastAPI
* Celery worker

Configure `backend/.env`, then:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

Remove local Docker persistence as well:

```bash
docker compose down -v
```

> `docker compose down -v` removes AIRIS's local PostgreSQL development volume. It does not modify the source MSSQL database.

# Frontend

## 5. Configure

In another terminal:

```bash
cd frontend
cp .env.example .env
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

Do not hard-code backend URLs in screens or components.

## 6. Install

```bash
npm install
```

## 7. Run

```bash
npm run start
```

Specific targets:

```bash
npm run web
npm run android
npm run ios
```

# API Overview

The API is versioned under:

```text
/api/v1
```

Current top-level route areas include:

| Area          | Prefix                  | Purpose                          |
| ------------- | ----------------------- | -------------------------------- |
| Health        | `/api/v1/health`        | Application/database health      |
| Database      | `/api/v1/database`      | Database discovery and metadata  |
| Analysis      | `/api/v1/analysis`      | Analysis operations              |
| Analysis Runs | `/api/v1/analysis-runs` | Analysis workflow/run state      |
| Modules       | `/api/v1/...`           | Domain-specific analysis modules |

Use `/docs` as the source of truth for exact endpoints and request/response schemas.

# Frontend Data Flow

Server data follows this path:

```text
Expo Route / Screen
        ↓
TanStack Query Hook
        ↓
API Domain Module
        ↓
Shared Axios Client
        ↓
FastAPI /api/v1/...
```

Frontend conventions:

* Screens do not call Axios directly.
* API URLs are centralized.
* TanStack Query owns server state.
* Zustand is used for client/UI state only.
* Loading, error, empty, and success states are handled.
* API contracts are typed in `src/types/`.
* Route files remain thin.
* Large datasets are paginated or virtualized.

# Large-Database Safety

AIRIS is built for a production database containing hundreds of tables. Never assume a table is small.

Prefer:

* metadata/catalog queries
* estimated counts where appropriate
* bounded queries
* configurable sampling
* server-side aggregates
* pagination
* conservative connection pools
* limited concurrency
* transferring only required data to Python

Avoid unrestricted queries such as:

```sql
SELECT *
FROM HugeTable;
```

Use an explicit bound or sampling strategy.

## MSSQL Read-Only Rule

The source MSSQL connection must never execute mutation operations such as:

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

Stored procedures must not be executed unless they are explicitly verified as read-only.

Use parameterized queries whenever values are involved.

# Development Commands

## Backend

```bash
cd backend

uv run pytest
uv run ruff check .
uv run ruff format .
uv run uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend

npm run typecheck
npm run lint
npm run start
npm run build:web
```

# Environment Variables

## Backend

| Variable              | Default                         | Purpose                       |
| --------------------- | ------------------------------- | ----------------------------- |
| `APP_NAME`            | `AIRIS Insights`                | Application name              |
| `APP_ENV`             | `development`                   | Runtime environment           |
| `APP_DEBUG`           | `true`                          | Debug mode                    |
| `MSSQL_HOST`          | empty                           | SQL Server host               |
| `MSSQL_PORT`          | `1433`                          | SQL Server port               |
| `MSSQL_DATABASE`      | empty                           | Source database               |
| `MSSQL_USERNAME`      | empty                           | Source DB user                |
| `MSSQL_PASSWORD`      | empty                           | Source DB password            |
| `MSSQL_DRIVER`        | `ODBC Driver 18 for SQL Server` | ODBC driver                   |
| `MSSQL_POOL_SIZE`     | `5`                             | MSSQL pool size               |
| `MSSQL_MAX_OVERFLOW`  | `2`                             | Additional pooled connections |
| `MSSQL_QUERY_TIMEOUT` | `30`                            | Query timeout                 |
| `POSTGRES_URL`        | `sqlite:///./dbinsights.db`     | AIRIS internal persistence    |
| `REDIS_URL`           | `redis://localhost:6379/0`      | Redis/Celery connection       |

Additional sampling and analysis settings live in `backend/app/core/config.py`.

## Frontend

| Variable              | Purpose                    |
| --------------------- | -------------------------- |
| `EXPO_PUBLIC_API_URL` | FastAPI `/api/v1` base URL |

`EXPO_PUBLIC_*` variables are bundled into the frontend. Never place secrets in them.

# Security

The source database may contain PII or other sensitive data.

Do not:

* commit credentials or populated `.env` files;
* log passwords or connection strings;
* log large source-data payloads;
* expose raw PII without a deliberate requirement;
* add source-database mutation paths;
* perform unrestricted production table scans.

Use least-privilege/read-only MSSQL credentials whenever possible.

# Engineering Rules

Repository-wide instructions:

```text
AGENTS.md
```

Implementation-specific instructions:

```text
backend/AGENTS.md
frontend/AGENTS.md
```

Core principles:

1. Inspect existing code before editing.
2. Keep changes focused.
3. Reuse existing architecture.
4. Keep backend/frontend contracts synchronized.
5. Never mutate source MSSQL.
6. Treat source data as sensitive.
7. Design every data operation for scale.
8. Keep types/contracts explicit.
9. Avoid unnecessary dependencies.
10. Run relevant tests, linting, and type checks.

# Development Status

AIRIS Insights is under active development around this core pipeline:

```text
Connect safely
      ↓
Discover database structure
      ↓
Inspect metadata
      ↓
Sample safely
      ↓
Profile and classify
      ↓
Run data-quality/domain analysis
      ↓
Persist structured results
      ↓
Present findings in the frontend
```

New functionality should extend this pipeline without bypassing its safety, data-volume, or architecture boundaries.

## Repository