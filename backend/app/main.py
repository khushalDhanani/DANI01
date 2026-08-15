from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import analysis, analysis_runs, database, health, modules
from app.core.exceptions import (
    DiscoveryError,
    ReadOnlyViolationError,
    TableNotFoundError,
)
from app.db.postgres import init_db


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
    return JSONResponse(
        status_code=404, content={"error": "TableNotFound", "detail": str(exc)}
    )


@app.exception_handler(ReadOnlyViolationError)
async def readonly_violation_handler(request: Request, exc: ReadOnlyViolationError):
    return JSONResponse(
        status_code=403, content={"error": "ReadOnlyViolation", "detail": str(exc)}
    )


@app.exception_handler(DiscoveryError)
async def discovery_error_handler(request: Request, exc: DiscoveryError):
    return JSONResponse(
        status_code=500, content={"error": "DiscoveryError", "detail": str(exc)}
    )


# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(database.router, prefix="/api/v1/database", tags=["Database"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(analysis_runs.router, prefix="/api/v1/analysis-runs", tags=["Analysis Runs"])
app.include_router(modules.router, prefix="/api/v1", tags=["Modules"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to AIRIS Insights API. Visit /docs for the API reference."
    }
