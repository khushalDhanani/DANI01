from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from app.classification.classifier import TableClassifier
from app.core.exceptions import (
    DiscoveryError,
    InvalidSortFieldError,
    TableNotFoundError,
)
from app.discovery.metadata import MetadataDiscovery
from app.profiling.profiler import TableProfiler
from app.sampling.sampler import TableSampler
from app.schemas.classification import TableClassificationResponse
from app.schemas.database import (
    ColumnListResponse,
    DatabaseSummary,
    IndexListResponse,
    SchemaListResponse,
    TableInfo,
    TableKeysResponse,
    TableListResponse,
    TableStructureResponse,
)
from app.schemas.profiling import TableProfileResponse
from app.schemas.sampling import TableSampleResponse

router = APIRouter()


def get_discovery_service() -> MetadataDiscovery:
    return MetadataDiscovery()


def get_sampling_service() -> TableSampler:
    return TableSampler()


def get_profiling_service() -> TableProfiler:
    return TableProfiler()


def get_classification_service() -> TableClassifier:
    return TableClassifier()


DiscoveryServiceDep = Annotated[MetadataDiscovery, Depends(get_discovery_service)]
SamplingServiceDep = Annotated[TableSampler, Depends(get_sampling_service)]
ProfilingServiceDep = Annotated[TableProfiler, Depends(get_profiling_service)]
ClassificationServiceDep = Annotated[TableClassifier, Depends(get_classification_service)]


@router.get("/summary", response_model=DatabaseSummary)
async def get_database_summary(
    service: DiscoveryServiceDep,
):
    """Returns high-level metadata summary including schema, table, column counts, and estimated rows."""
    try:
        return service.get_database_summary()
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schemas", response_model=SchemaListResponse)
async def get_schemas(
    service: DiscoveryServiceDep,
):
    """Returns a list of non-system schemas and their table counts."""
    try:
        return service.get_schemas()
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables", response_model=TableListResponse)
async def get_tables(
    service: DiscoveryServiceDep,
    schema: str | None = Query(default=None, description="Filter by schema name"),
    search: str | None = Query(default=None, description="Search tables by name"),
    limit: int = Query(default=100, ge=1, le=1000, description="Max items to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    sort_by: Literal["schema", "table", "estimated_rows", "column_count"] = Query(
        default="table", description="Field to sort by"
    ),
    sort_order: Literal["asc", "desc"] = Query(default="asc", description="Sort order (asc/desc)"),
):
    """Discovers tables with pagination, schema filtering, search filtering, and safe sorting."""
    try:
        return service.get_tables(
            schema=schema,
            search=search,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except InvalidSortFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tables/{schema_name}/{table_name}", response_model=TableInfo)
async def get_table(
    schema_name: str,
    table_name: str,
    service: DiscoveryServiceDep,
):
    """Returns metadata for a specific table."""
    try:
        return service.get_table(schema_name, table_name)
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tables/{schema_name}/{table_name}/columns",
    response_model=ColumnListResponse,
)
async def get_table_columns(
    schema_name: str,
    table_name: str,
    service: DiscoveryServiceDep,
):
    """Returns column specifications for a specific table."""
    try:
        return service.get_column_list_response(schema_name, table_name)
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tables/{schema_name}/{table_name}/keys",
    response_model=TableKeysResponse,
)
async def get_table_keys(
    schema_name: str,
    table_name: str,
    service: DiscoveryServiceDep,
):
    """Returns Primary Key and Foreign Keys for a specific table."""
    try:
        return service.get_table_keys(schema_name, table_name)
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tables/{schema_name}/{table_name}/indexes",
    response_model=IndexListResponse,
)
async def get_table_indexes(
    schema_name: str,
    table_name: str,
    service: DiscoveryServiceDep,
):
    """Returns indexes and included columns for a specific table."""
    try:
        return service.get_index_list_response(schema_name, table_name)
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tables/{schema_name}/{table_name}/structure",
    response_model=TableStructureResponse,
)
async def get_table_structure(
    schema_name: str,
    table_name: str,
    service: DiscoveryServiceDep,
):
    """Returns full structural definition (table info, columns, keys, indexes)."""
    try:
        return service.get_table_structure(schema_name, table_name)
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tables/{schema_name}/{table_name}/sample",
    response_model=TableSampleResponse,
)
async def sample_table(
    schema_name: str,
    table_name: str,
    service: SamplingServiceDep,
    limit: int = Query(default=100, ge=1, le=10000, description="Max rows to sample"),
):
    """Returns a safe, bounded row sample for a table."""
    try:
        return service.sample(schema_name, table_name, limit=limit)
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tables/{schema_name}/{table_name}/profile",
    response_model=TableProfileResponse,
)
async def profile_table(
    schema_name: str,
    table_name: str,
    service: ProfilingServiceDep,
    limit: int = Query(default=1000, ge=1, le=10000, description="Sample size to profile"),
):
    """Generates an in-memory statistical profile of a table using Polars."""
    try:
        return service.profile_table(schema_name, table_name, limit=limit)
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tables/{schema_name}/{table_name}/classification",
    response_model=TableClassificationResponse,
)
async def classify_table(
    schema_name: str,
    table_name: str,
    service: ClassificationServiceDep,
):
    """Performs semantic column classification on a table."""
    try:
        return service.classify_table(schema_name, table_name)
    except TableNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))
