"""Pydantic schemas for Python version tracking."""

from datetime import datetime
from pydantic import BaseModel, Field


class PythonReleaseInfo(BaseModel):
    """Information about a Python release."""
    version: str = Field(..., description="Python version (e.g., 3.12.1)")
    major: int = Field(..., description="Major version number")
    minor: int = Field(..., description="Minor version number")
    patch: int = Field(..., description="Patch version number")
    release_date: datetime = Field(..., description="Date when the version was released")
    release_notes_url: str = Field(..., description="URL to release notes")
    changelog: str = Field("", description="Changelog content extracted from release notes")
    is_stable: bool = Field(..., description="Whether this is a stable release")
    eol_date: datetime | None = Field(None, description="End of Life date for this version")
    is_major_bump: bool = Field(False, description="Whether this is a major version bump")
    is_minor_bump: bool = Field(False, description="Whether this is a minor version bump")


class PythonVersionsListResponse(BaseModel):
    """Response for Python versions list."""
    versions: list[PythonReleaseInfo] = Field(..., description="List of Python versions")
    total_count: int = Field(..., description="Total number of versions")
    include_all_releases: bool = Field(
        False,
        description="Whether the list includes all releases or only stable ones"
    )
    time_range_years: int = Field(10, description="Number of years of versions included")


class VersionComparison(BaseModel):
    """Comparison between two Python versions."""
    from_version: str = Field(..., description="Starting version")
    to_version: str = Field(..., description="Target version")
    from_release_date: datetime = Field(..., description="Release date of from_version")
    to_release_date: datetime = Field(..., description="Release date of to_version")
    days_between: int = Field(..., description="Days between releases")
    major_bumps: int = Field(0, description="Number of major version bumps")
    minor_bumps: int = Field(0, description="Number of minor version bumps")
    patch_bumps: int = Field(0, description="Number of patch version bumps")
    versions_in_between: list[str] = Field(
        default_factory=list,
        description="List of versions between from_version and to_version"
    )


class PythonVersionsComparisonResponse(BaseModel):
    """Response for version comparison."""
    comparison: VersionComparison = Field(..., description="Comparison details")
    changes_summary: str = Field(..., description="Human-readable summary of changes")
