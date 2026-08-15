from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.analysis.database_analyzer import DatabaseAnalyzer
from app.api.dependencies import get_database_analyzer
from app.core.exceptions import DiscoveryError
from app.schemas.analysis import DatabaseAnalysisResponse, QuickAnalysisRequest

router = APIRouter()

DatabaseAnalyzerDep = Annotated[DatabaseAnalyzer, Depends(get_database_analyzer)]


@router.post("/quick", response_model=DatabaseAnalysisResponse)
async def run_quick_analysis(
    request: QuickAnalysisRequest = QuickAnalysisRequest(),
    analyzer: DatabaseAnalyzerDep = None,
):
    """
    Executes database-wide QUICK analysis orchestration across all eligible tables.
    Composes V1 Discovery, V2 Structure, V3 Sampling, V4 Profiling, and V5 Semantic Classification.
    """
    try:
        return await analyzer.analyze_database(
            schema=request.schema_name,
            max_concurrent=request.max_concurrent,
        )
    except DiscoveryError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database analysis failed: {str(e)}"
        )
