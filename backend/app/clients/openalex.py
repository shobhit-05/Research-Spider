import logging
from typing import List, Optional

import httpx

from ..config import get_settings
from ..models import PaperMetadata

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openalex.org"


class OpenAlexClient:
    def __init__(self, email: Optional[str] = None, timeout: int = 15) -> None:
        settings = get_settings()
        self.email = email or settings.openalex_email
        self.timeout = timeout or settings.request_timeout

    def _params(self) -> dict:
        params: dict = {}
        if self.email:
            params["mailto"] = self.email
        return params

    async def search_by_title(
        self, title: str, limit: int = 5
    ) -> List[PaperMetadata]:
        if not title:
            return []
        params = {
            **self._params(),
            "search": title,
            "per-page": limit,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{BASE_URL}/works", params=params)
                response.raise_for_status()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("OpenAlex title search failed: %s", exc)
                return []
        works = response.json().get("results", [])
        return [self._to_metadata(item) for item in works if item]

    async def related_by_authors(
        self, authors: List[str], limit: int = 5
    ) -> List[PaperMetadata]:
        if not authors:
            return []
        author = authors[0]
        params = {
            **self._params(),
            "filter": f"authorships.author.display_name.search:{author}",
            "per-page": limit,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{BASE_URL}/works", params=params)
                response.raise_for_status()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("OpenAlex author search failed: %s", exc)
                return []
        works = response.json().get("results", [])
        return [self._to_metadata(item) for item in works if item]

    async def fetch_by_doi(self, doi: str) -> Optional[PaperMetadata]:
        if not doi:
            return None
        url = f"{BASE_URL}/works/https://doi.org/{doi}"
        params = self._params()
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("OpenAlex DOI fetch failed: %s", exc)
                return None
        return self._to_metadata(response.json())

    def _to_metadata(self, payload: dict) -> Optional[PaperMetadata]:
        if not payload:
            return None
        ids = payload.get("ids", {})
        doi = ids.get("doi")
        oa_id = payload.get("id")
        authorships = payload.get("authorships") or []
        authors = []
        for a in authorships:
            author = a.get("author", {})
            name = author.get("display_name")
            if name:
                authors.append(name)
        biblio = payload.get("biblio") or {}
        year = biblio.get("year_published") or payload.get("publication_year")
        return PaperMetadata(
            id=doi or oa_id or payload.get("doi", ""),
            title=payload.get("display_name") or payload.get("title") or "Untitled",
            abstract=None,
            authors=authors,
            year=year,
            pdf_link=None,
            keywords=[],
            source="openalex",
            references=[],
        )
