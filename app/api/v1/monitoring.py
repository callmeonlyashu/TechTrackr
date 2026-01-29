from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str


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
        HealthCheckResponse: Status of the service.
    """
    return HealthCheckResponse(status="healthy")