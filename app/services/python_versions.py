"""Service for fetching and processing Python version data from GitHub."""

import logging
from datetime import datetime, timedelta
import httpx
from packaging import version

from app.schemas.versions import (
    PythonReleaseInfo,
    PythonVersionsListResponse,
    VersionComparison,
    PythonVersionsComparisonResponse,
)

# Import the scraper for python.org cached data
from app.services.python_org_scraper import PythonOrgScraper

logger = logging.getLogger(__name__)

# Known EOL dates for Python versions (source: https://devguide.python.org/versions/)
PYTHON_EOL_DATES: dict[str, datetime] = {
    "3.8": datetime(2024, 10, 31),
    "3.9": datetime(2025, 10, 31),
    "3.10": datetime(2026, 10, 4),
    "3.11": datetime(2027, 10, 24),
    "3.12": datetime(2028, 10, 2),
    "3.13": datetime(2029, 10, 31),
}


class PythonVersionService:
    """Service to fetch and process Python versions from GitHub."""
    
    GITHUB_API_URL = "https://api.github.com/repos/python/cpython/releases"
    GITHUB_HEADERS = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    @staticmethod
    async def get_python_versions(
        include_all_releases: bool = False,
        years: int = 10,
    ) -> PythonVersionsListResponse:
        """
        Fetch Python versions from GitHub API.
        
        Args:
            include_all_releases: If True, include alpha, beta, rc releases.
                                If False, only stable releases.
            years: Number of years to look back from today.
            
        Returns:
            PythonVersionsListResponse with list of versions.
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Fetch all releases from GitHub
                all_releases = []
                page = 1
                per_page = 100
                
                while True:
                    response = await client.get(
                        PythonVersionService.GITHUB_API_URL,
                        params={"per_page": per_page, "page": page},
                        headers=PythonVersionService.GITHUB_HEADERS
                    )
                    
                    if response.status_code == 404:
                        logger.error("GitHub repository not found")
                        raise ValueError("Python cpython repository not found on GitHub")
                    
                    response.raise_for_status()
                    releases = response.json()
                    
                    if not releases:
                        break
                    
                    all_releases.extend(releases)
                    
                    # If we got less than per_page results, we're at the end
                    if len(releases) < per_page:
                        break
                    
                    page += 1
                
                # Process releases
                cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
                processed_versions: list[PythonReleaseInfo] = []
                prev_version = None
                
                # for release in all_releases:
                # Try loading cached scraped data first; if empty, trigger scraping
                processed_versions: list[PythonReleaseInfo] = []
                try:
                    cached = PythonOrgScraper.load_cached()
                    if not cached:
                        cached = await PythonOrgScraper.scrape_and_cache(years=years, include_all_releases=include_all_releases)

                    for item in cached:
                        ver = item.get("version", "")
                        try:
                            parsed = version.parse(ver)
                            if not isinstance(parsed, version.Version):
                                continue
                        except Exception:
                            continue

                        release_date = None
                        try:
                            release_date = datetime.fromisoformat(item.get("release_date", ""))
                        except Exception:
                            continue

                        major_minor = ".".join(str(parsed).split('.')[:2])
                        eol_date = item.get("eol_date") or PYTHON_EOL_DATES.get(major_minor)

                        release_info = PythonReleaseInfo(
                            version=ver,
                            major=parsed.major,
                            minor=parsed.minor,
                            patch=parsed.micro,
                            release_date=release_date,
                            release_notes_url=item.get("release_notes_url", ""),
                            changelog=item.get("changelog", ""),
                            is_stable=True,
                            eol_date=eol_date,
                            is_major_bump=False,
                            is_minor_bump=False,
                        )

                        processed_versions.append(release_info)

                    # mark major/minor bumps
                    prev = None
                    for rv in processed_versions:
                        if prev:
                            if rv.major > prev.major:
                                rv.is_major_bump = True
                            elif rv.minor > prev.minor:
                                rv.is_minor_bump = True
                        prev = rv

                    return PythonVersionsListResponse(
                        versions=processed_versions,
                        total_count=len(processed_versions),
                        include_all_releases=include_all_releases,
                        time_range_years=years,
                    )
                except Exception as e:
                    logger.error(f"Error loading scraped Python versions: {e}")
                    raise
            if v.version == to_version:
                to_info = v

        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub API error: {e}")
            raise ValueError("Failed to fetch Python versions from GitHub") from e
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise ValueError("An unexpected error occurred while fetching Python versions") from e
        
        if not from_info or not to_info:
            missing = []
            if not from_info:
                missing.append(from_version)
            if not to_info:
                missing.append(to_version)
            raise ValueError(f"Version(s) not found: {', '.join(missing)}")
        
        # Get versions in between
        versions_in_between = []
        from_idx = all_versions.index(from_info)
        to_idx = all_versions.index(to_info)
        
        # Handle both ascending and descending comparisons
        if from_idx < to_idx:
            for i in range(from_idx + 1, to_idx):
                versions_in_between.append(all_versions[i].version)
        else:
            for i in range(to_idx + 1, from_idx):
                versions_in_between.append(all_versions[i].version)
        
        # Count version bumps
        major_bumps = 0
        minor_bumps = 0
        patch_bumps = 0
        
        if from_idx < to_idx:
            for i in range(from_idx, to_idx):
                v1 = all_versions[i]
                v2 = all_versions[i + 1]
                
                if v2.major > v1.major:
                    major_bumps += 1
                elif v2.minor > v1.minor:
                    minor_bumps += 1
                else:
                    patch_bumps += 1
        else:
            for i in range(to_idx, from_idx):
                v1 = all_versions[i]
                v2 = all_versions[i + 1]
                
                if v2.major > v1.major:
                    major_bumps += 1
                elif v2.minor > v1.minor:
                    minor_bumps += 1
                else:
                    patch_bumps += 1
        
        days_between = abs((to_info.release_date - from_info.release_date).days)
        
        comparison = VersionComparison(
            from_version=from_version,
            to_version=to_version,
            from_release_date=from_info.release_date,
            to_release_date=to_info.release_date,
            days_between=days_between,
            major_bumps=major_bumps,
            minor_bumps=minor_bumps,
            patch_bumps=patch_bumps,
            versions_in_between=versions_in_between,
        )
        
        changes_summary = (
            f"Between {from_version} and {to_version}: "
            f"{major_bumps} major bumps, {minor_bumps} minor bumps, {patch_bumps} patch bumps. "
            f"Released {days_between} days apart. "
            f"{len(versions_in_between)} versions in between."
        )
        
        return PythonVersionsComparisonResponse(
            comparison=comparison,
            changes_summary=changes_summary,
        )

