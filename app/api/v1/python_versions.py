"""Python version tracking and comparison endpoints."""

from fastapi import APIRouter, Query

from app.services.python_versions import PythonVersionService
from app.schemas.versions import (
    PythonVersionsListResponse,
    PythonVersionsComparisonResponse,
)

router = APIRouter(prefix="/python-versions", tags=["Python Versions"])


@router.get(
    "",
    response_model=PythonVersionsListResponse,
    status_code=200,
    summary="Get Python Versions",
    description="Fetch all Python versions from GitHub with major/minor version bump tracking.",
)
async def get_python_versions(
    include_all_releases: bool = Query(
        False,
        description="Include pre-releases (alpha, beta, rc). Default: stable releases only."
    ),
    years: int = Query(
        10,
        ge=1,
        le=30,
        description="Number of years to look back. Default: 10 years."
    ),
) -> PythonVersionsListResponse:
    """
    Get all Python versions from GitHub with version bump indicators.
    
    Shows major and minor version bumps for each release.
    Includes release dates and EOL information.
    
    Query Parameters:
        include_all_releases: If True, includes alpha/beta/rc releases.
        years: Number of years to look back (1-30).
    
    Returns:
        PythonVersionsListResponse: List of versions with bump indicators.
    """
    return await PythonVersionService.get_python_versions(
        include_all_releases=include_all_releases,
        years=years,
    )

