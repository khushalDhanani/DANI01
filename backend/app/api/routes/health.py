from fastapi import APIRouter

from app.core.config import settings
from app.db.mssql import test_connection

router = APIRouter()


@router.get("")
async def check_health():
    return {"status": "ok", "service": settings.APP_NAME}


@router.get("/database")
async def check_database_health():
    is_connected = test_connection()
    if is_connected:
        return {"status": "ok", "database": "connected"}
    else:
        return {"status": "error", "database": "disconnected"}
