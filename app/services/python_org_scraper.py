"""Scrape python.org downloads and cache results as JSON.

Saves to `data/python/filenamebestsuited.json` and returns structured release info.
"""

import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

DATA_DIR = Path("data/python")
# Standardized cache filename used by services
DATA_FILE = DATA_DIR / "python_release_info.json"
PYTHON_DOWNLOADS_URL = "https://www.python.org/downloads/"
EOL_API = "https://endoflife.date/api/python.json"


class PythonOrgScraper:
    @staticmethod
    async def fetch_eol_map() -> dict[str, str]:
        """Fetch EOL data from endoflife.date and return map major.minor -> eol_date (ISO).
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(EOL_API)
                r.raise_for_status()
                data = r.json()
                m: dict[str, str] = {}
                for row in data:
                    version = row.get("version")
                    eol = row.get("eol")
                    if version and eol:
                        # version like "3.10" or "3.11"
                        m[version] = eol
                return m
        except Exception as e:
            logger.debug(f"Could not fetch EOL data: {e}")
            return {}

    @staticmethod
    def _parse_version_from_text(text: str) -> str | None:
        m = re.search(r"Python\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)", text)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def _parse_date_from_text(text: str) -> datetime | None:
        # Try to find a date-like substring
        try:
            # dateutil can parse many formats
            dt = date_parser.parse(text, fuzzy=True)
            return dt
        except Exception:
            return None

    @staticmethod
    async def _fetch_changelog(url: str, timeout: float = 10.0) -> str:
        """Fetch and extract changelog text from a URL.
        
        Args:
            url: URL to fetch changelog from
            timeout: Request timeout in seconds
            
        Returns:
            Extracted changelog text (truncated to 5000 chars if too long)
        """
        if not url:
            return ""
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.get(url)
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")
                
                # Remove script and style tags
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extract text
                text = soup.get_text(separator="\n", strip=True)
                
                # Clean up excessive whitespace
                text = "\n".join(line.strip() for line in text.split("\n") if line.strip())
                
                # Truncate if too long (keep first 5000 chars to avoid huge JSON)
                if len(text) > 5000:
                    text = text[:5000] + "..."
                
                return text
        except Exception as e:
            logger.debug(f"Could not fetch changelog from {url}: {e}")
            return ""


    @staticmethod
    async def scrape_and_cache(years: int = 10, include_all_releases: bool = False) -> list[dict]:
        """Scrape python.org downloads page and cache JSON to DATA_FILE.

        Returns list of dicts with keys: version, release_date (ISO), release_notes_url, eol_date
        """
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        cutoff = datetime.utcnow() - timedelta(days=years * 365)

        eol_map = await PythonOrgScraper.fetch_eol_map()

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(PYTHON_DOWNLOADS_URL)
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")

                anchors = soup.find_all("a", href=re.compile(r"/downloads/release/python-"))
                seen = set()
                releases = []

                for a in anchors:
                    href = a.get("href")
                    if not href or href in seen:
                        continue
                    seen.add(href)

                    version = PythonOrgScraper._parse_version_from_text(a.get_text() or "")
                    if not version:
                        continue

                    parent_text = a.parent.get_text(separator=" ") if a.parent else a.get_text()
                    release_date = PythonOrgScraper._parse_date_from_text(parent_text)
                    if not release_date:
                        # try following sibling text
                        sibling_text = " ".join([s.strip() for s in a.parent.strings]) if a.parent else a.get_text()
                        release_date = PythonOrgScraper._parse_date_from_text(sibling_text)

                    if not release_date:
                        continue

                    if release_date < cutoff:
                        # older than range; skip
                        continue

                    # Find a "Release notes" link near this anchor
                    release_notes_url = None
                    # Search within parent or next siblings
                    rel_notes = a.parent.find_next("a", string=re.compile(r"Release notes", re.I)) if a.parent else None
                    if rel_notes and rel_notes.get("href"):
                        release_notes_url = rel_notes.get("href")
                    else:
                        # fallback: try to find a docs link pattern
                        rel = soup.find("a", href=re.compile(r"docs.python.org"))
                        if rel:
                            release_notes_url = rel.get("href")

                    if release_notes_url and release_notes_url.startswith("/"):
                        release_notes_url = "https://www.python.org" + release_notes_url

                    major_minor = ".".join(version.split('.')[:2])
                    eol_date = eol_map.get(major_minor)

                    # Fetch changelog content from release notes URL
                    # changelog = await PythonOrgScraper._fetch_changelog(release_notes_url)

                    releases.append({
                        "version": version,
                        "release_date": release_date.isoformat(),
                        "release_notes_url": release_notes_url or "",
                        "changelog": "",  # Commented out web scraping for now
                        "eol_date": eol_date,
                    })

                # Sort releases by release_date descending
                releases.sort(key=lambda r: r.get("release_date", ""), reverse=True)

                # Save to cache
                try:
                    with DATA_FILE.open("w", encoding="utf-8") as f:
                        json.dump({"generated_at": datetime.utcnow().isoformat(), "releases": releases}, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    logger.debug(f"Failed to write cache file: {e}")

                return releases
        except Exception as e:
            logger.error(f"Error scraping python.org: {e}")
            # If scraping fails but cache exists, try loading cache
            if DATA_FILE.exists():
                try:
                    with DATA_FILE.open("r", encoding="utf-8") as f:
                        payload = json.load(f)
                        return payload.get("releases", [])
                except Exception:
                    return []
            return []

    @staticmethod
    def load_cached() -> list[dict]:
        if not DATA_FILE.exists():
            return []
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                payload = json.load(f)
                return payload.get("releases", [])
        except Exception as e:
            logger.debug(f"Failed to load cache: {e}")
            return []
