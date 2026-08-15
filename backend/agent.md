# AIRIS AIRIS Insights Backend — Agent Instructions

## Project

**Project:** AIRIS Insights / AIRIS Insights
**Scope:** Backend only
**Language:** Python 3.12+
**Package Manager:** `uv`

The backend analyzes an existing Microsoft SQL Server database containing approximately **900+ tables**.

The source MSSQL database is production data and must always be treated as **READ ONLY**.

---

## Core Rule

### NEVER modify the source MSSQL database.

The backend must never execute:

* `INSERT`
* `UPDATE`
* `DELETE`
* `MERGE`
* `TRUNCATE`
* `ALTER`
* `DROP`
* `CREATE`

Do not create temporary/business tables inside the source database.

Do not execute stored procedures unless they are explicitly verified to be read-only.

Prefer:

```sql
SELECT ...
```

and SQL Server metadata/system catalog queries.

All source DB access must use parameterized queries where values are involved.

---

# Tech Stack

Use the following stack unless there is a strong technical reason to change it:

```text
Python 3.12+
uv

FastAPI
Pydantic v2
pydantic-settings

SQLAlchemy 2.x
pyodbc
Microsoft ODBC Driver 18

Polars
NumPy

PostgreSQL        # AIRIS Insights internal data
Alembic

Celery            # later/background processing
Redis             # later/job broker/cache

pytest
Ruff
Docker
```

Do not introduce additional frameworks without a clear requirement.

Avoid premature use of:

* Spark
* Kafka
* Kubernetes
* Airflow
* Elasticsearch
* Vector databases
* Microservices

The backend should begin as a **modular monolith**.

---

# Current Project Root

```text
AIRIS_INSIGHTS/
└── backend/
    ├── .venv/
    ├── .gitignore
    ├── .python-version
    ├── main.py
    ├── pyproject.toml
    ├── README.md
    └── uv.lock
```

Gradually move application code toward:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── db/
│   │   ├── mssql.py
│   │   └── postgres.py
│   │
│   ├── discovery/
│   │
│   ├── profiling/
│   │
│   ├── analysis/
│   │
│   ├── models/
│   │
│   └── workers/
│
├── tests/
├── pyproject.toml
├── uv.lock
├── .env.example
└── README.md
```

Do not create empty architecture folders unless they are about to be used.

---

# Architecture Rules

Keep responsibilities separated.

## `api/`

FastAPI HTTP layer only.

Responsible for:

* request parsing
* validation
* authentication later
* calling application/services
* returning responses

Do **not** place SQL queries or profiling logic inside API routes.

---

## `core/`

Application-wide infrastructure.

Examples:

* configuration
* logging
* exceptions
* constants
* application lifecycle

Use `pydantic-settings` for configuration.

Never hard-code secrets.

---

## `db/`

Database connectivity.

### `db/mssql.py`

Responsible for:

* MSSQL engine creation
* connection pooling
* connection testing
* connection lifecycle
* read-only execution helpers

Do not place business analysis logic here.

### `db/postgres.py`

Used for AIRIS Insights' own persistence.

Source MSSQL and internal PostgreSQL are separate systems.

---

## `discovery/`

Responsible for understanding the MSSQL database structure.

Examples:

* schemas
* tables
* columns
* primary keys
* foreign keys
* indexes
* estimated row counts
* relationships

Prefer SQL Server catalog views and metadata queries over expensive table scans.

---

## `profiling/`

Responsible for analyzing table/column data.

Examples:

* sampling
* null statistics
* distinct statistics
* string lengths
* numeric distributions
* date ranges
* common values
* semantic type inference

Use **Polars** for Python-side profiling.

Do not automatically load entire tables into Python.

---

## `analysis/`

Coordinates analysis workflows.

Example:

```text
QuickAnalysis
    ↓
Discover table
    ↓
Get metadata
    ↓
Determine sample strategy
    ↓
Fetch sample
    ↓
Profile columns
    ↓
Generate results
```

Analysis code should not depend directly on FastAPI.

Analysis code should also not depend directly on Celery.

---

# MSSQL Performance Rules

There are approximately **900+ tables**.

Never assume a table is small.

Before expensive analysis, determine:

* estimated row count
* column count
* table size where possible
* available indexes
* primary key

Never use:

```sql
SELECT *
FROM HugeTable
```

without an explicit controlled row limit.

Use sampling.

Typical quick-analysis sample target:

```text
Small tables       → full / near full
Medium tables      → ~5,000 rows
Large tables       → ~10,000 rows
Very large tables  → ~10,000–25,000 rows
```

Sample sizes must ultimately be configurable.

Prefer SQL Server for simple aggregates such as:

* row counts
* NULL counts
* MIN
* MAX

Prefer Python/Polars for:

* sample profiling
* pattern detection
* semantic classification
* complex analysis

Minimize data transferred from MSSQL to Python.

---

# Connection Pool Rules

Start conservatively.

Example target:

```text
pool_size       = 5
max_overflow    = 2–5
query_timeout   = configurable
```

Do not create large numbers of concurrent MSSQL queries.

Protect the production server before optimizing scan speed.

---

# Quick Analysis V1

The first implementation should focus only on **Quick Analysis**.

## Table information

Collect:

* schema name
* table name
* estimated row count
* column count
* PK
* FK
* index information

## Column information

Collect where practical:

* name
* SQL datatype
* nullable
* identity
* computed
* PK/FK participation
* NULL %
* empty %
* distinct estimate/sample %
* min/max
* string length statistics
* common values
* possible semantic type

Possible semantic types include:

```text
EMAIL
PHONE
URL
NAME
ADDRESS
CITY
STATE
COUNTRY
POSTAL_CODE
DATE
DATETIME
AMOUNT
IDENTIFIER
STATUS
UNKNOWN
```

Do not build advanced duplicate detection or AI features before Quick Analysis works reliably.

---

# Error Handling

Do not use broad silent exceptions such as:

```python
try:
    ...
except Exception:
    pass
```

Failures should be visible and logged.

Prefer application-specific exceptions such as:

```text
DBInsightsError
ConnectorError
MSSQLConnectionError
QueryExecutionError
QueryTimeoutError
ReadOnlyViolationError
DiscoveryError
ProfilingError
AnalysisError
```

A failure analyzing one table must not crash analysis of the entire database.

---

# Logging

Use structured logging.

Useful context includes:

```text
request_id
analysis_run_id
database
schema
table
operation
duration_ms
row_count
sample_size
```

Never log:

* passwords
* connection strings containing passwords
* secrets
* large source data payloads
* sensitive record contents unnecessarily

---

# Configuration

Configuration belongs in environment variables and Pydantic Settings.

Example:

```text
APP_ENV
APP_DEBUG

MSSQL_HOST
MSSQL_PORT
MSSQL_DATABASE
MSSQL_USERNAME
MSSQL_PASSWORD
MSSQL_DRIVER

MSSQL_POOL_SIZE
MSSQL_MAX_OVERFLOW
MSSQL_QUERY_TIMEOUT

PROFILE_SAMPLE_SIZE
PROFILE_MAX_SAMPLE_SIZE
```

Maintain `.env.example`.

Never commit `.env` containing secrets.

---

# Python Coding Standards

Use:

* type hints
* small focused functions
* descriptive names
* dependency injection where useful
* async only when it provides actual benefit
* Pydantic models for API contracts
* SQLAlchemy for connection management
* parameterized SQL

Avoid:

* giant service classes
* generic `utils.py`
* duplicated SQL
* global mutable state
* hidden side effects
* business logic in route functions

Prefer:

```python
def profile_column(...) -> ColumnProfile:
    ...
```

over untyped functions returning arbitrary dictionaries when the structure is known.

---

# API Conventions

Use versioned routes:

```text
/api/v1/...
```

Initial endpoints may include:

```text
GET  /api/v1/health
GET  /api/v1/database
GET  /api/v1/schemas
GET  /api/v1/tables
GET  /api/v1/tables/{table_name}
POST /api/v1/analysis/quick
GET  /api/v1/analysis/{run_id}
```

API routes should call services; they should not perform analysis themselves.

---

# Testing

Use `pytest`.

**STRICT RULE:** Any test scripts, connection tests, or experimental test files must ONLY be created inside the `tests/` directory. Do not create one-off test files (e.g., `test_conn.py`) in the project root.

At minimum test:

* configuration
* MSSQL connection handling
* read-only protections
* metadata discovery
* sampling
* profiling
* API health endpoint
* error handling

Critical safety tests must prove that modification SQL is rejected.

Never run destructive tests against production MSSQL.

---

# Development Commands

Install dependencies:

```bash
uv sync
```

Add package:

```bash
uv add <package>
```

Add development dependency:

```bash
uv add --dev <package>
```

Run application:

```bash
uv run uvicorn app.main:app --reload
```

Run tests:

```bash
uv run pytest
```

Run Ruff:

```bash
uv run ruff check .
```

Format:

```bash
uv run ruff format .
```

---

# Implementation Priority

Work in this order unless explicitly instructed otherwise:

```text
1. FastAPI application foundation
2. Configuration
3. MSSQL read-only connection
4. Health / connection test
5. Schema discovery
6. Table discovery
7. Column discovery
8. PK / FK / index discovery
9. Safe sampling
10. Polars profiling
11. Quick Analysis orchestration
12. PostgreSQL result persistence
13. Background jobs
14. Celery / Redis
15. Advanced analysis
```

Do not jump ahead to advanced architecture while core MSSQL discovery and profiling are incomplete.

---

# Agent Behavior

When modifying this project:

1. Inspect existing code before creating new files.
2. Reuse existing modules where appropriate.
3. Do not unnecessarily reorganize working code.
4. Keep changes focused on the requested task.
5. Avoid introducing dependencies unless necessary.
6. Maintain read-only MSSQL guarantees.
7. Consider production DB performance for every query.
8. Do not perform unrestricted full-table scans.
9. Add/update tests for important behavior.
10. Keep the implementation understandable for future engineers.

When uncertain between a sophisticated solution and a simpler reliable solution, prefer the simpler solution that preserves scalability and safety.

## Primary Goal

Build a backend that can safely answer:

> **What exists in this MSSQL database, what does the data look like, and where should deeper analysis be performed?**

The first milestone is:

```text
Connect safely
    ↓
Discover 900+ tables
    ↓
Discover their structure
    ↓
Sample safely
    ↓
Run Quick Analysis
    ↓
Return structured results
```

Everything else should build on top of this pipeline.
