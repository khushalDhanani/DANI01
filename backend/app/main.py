import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import analysis, analysis_runs, campaign, database, health, modules
from app.core.exceptions import (
    DatabaseConnectionError,
    DiscoveryError,
    ReadOnlyViolationError,
    TableNotFoundError,
)
from app.db.postgres import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure persistence tables exist on startup
    init_db()
    yield


app = FastAPI(
    title="AIRIS Insights API",
    description="Backend API for AIRIS Insights Platform (MSSQL Metadata & Profiling)",
    version="1.0.0",
    lifespan=lifespan,
)


# Exception handlers
@app.exception_handler(TableNotFoundError)
async def table_not_found_handler(request: Request, exc: TableNotFoundError):
    return JSONResponse(status_code=404, content={"error": "TableNotFound", "detail": str(exc)})


@app.exception_handler(ReadOnlyViolationError)
async def readonly_violation_handler(request: Request, exc: ReadOnlyViolationError):
    return JSONResponse(status_code=403, content={"error": "ReadOnlyViolation", "detail": str(exc)})


@app.exception_handler(DatabaseConnectionError)
async def database_connection_handler(request: Request, exc: DatabaseConnectionError):
    logger.warning("Database connection unavailable on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=503,
        content={
            "error": "DatabaseConnectionError",
            "detail": f"MSSQL database is unavailable or not initialized: {exc}",
        },
    )


@app.exception_handler(DiscoveryError)
async def discovery_error_handler(request: Request, exc: DiscoveryError):
    return JSONResponse(status_code=500, content={"error": "DiscoveryError", "detail": str(exc)})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled API exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "detail": str(exc)},
    )


# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:19006",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:19006",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(database.router, prefix="/api/v1/database", tags=["Database"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(analysis_runs.router, prefix="/api/v1/analysis-runs", tags=["Analysis Runs"])
app.include_router(campaign.router, prefix="/api/v1/campaigns", tags=["Campaigns"])
app.include_router(modules.router, prefix="/api/v1", tags=["Modules"])


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to AIRIS Insights API. Visit /docs for the API reference."}
