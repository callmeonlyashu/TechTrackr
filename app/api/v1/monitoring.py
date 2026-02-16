import sys
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.database import check_db_connection

router = APIRouter()


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: str
    python_version: str
    platform: str
    database: str


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=200,
    tags=["Monitoring"],
    summary="Health Check",
    description="Check if the API service is running and healthy, including database connectivity.",
)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint to verify API service availability and database connection.
    
    Returns:
        HealthCheckResponse: Status of the service with system information and database health.
    """
    db_connected = await check_db_connection()
    db_status = "connected" if db_connected else "disconnected"
    
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        platform=sys.platform,
        database=db_status,
    )
