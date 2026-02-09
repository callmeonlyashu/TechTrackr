import sys
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str
    timestamp: str
    python_version: str
    platform: str


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=200,
    tags=["Monitoring"],
    summary="Health Check",
    description="Check if the API service is running and healthy.",
)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint to verify API service availability.
    
    Returns:
        HealthCheckResponse: Status of the service with system information.
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        platform=sys.platform,
    )
