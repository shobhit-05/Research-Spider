import logging
from typing import List, Optional

import httpx

from ..config import get_settings
from ..models import PaperMetadata

logger = logging.getLogger(__name__)

BASE_URL = "https://api.semanticscholar.org/graph/v1"


class SemanticScholarClient:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 15) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.semantic_scholar_api_key
        self.timeout = timeout or settings.request_timeout

    def _headers(self) -> dict:
        headers: dict = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    async def fetch_paper(self, identifier: str) -> Optional[PaperMetadata]:
        url = f"{BASE_URL}/paper/{identifier}"
        params = {
            "fields": "title,abstract,year,authors.name,externalIds,openAccessPdf,url,referenceCount,citationCount"
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params, headers=self._headers())
                response.raise_for_status()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Semantic Scholar fetch failed: %s", exc)
                return None
        data = response.json()
        return self._to_metadata(data)

    async def search_by_keywords(
        self, keywords: List[str], limit: int = 5
    ) -> List[PaperMetadata]:
        if not keywords:
            return []
        query = " ".join(keywords)
        params = {
            "query": query,
            "offset": 0,
            "limit": limit,
            "fields": "title,abstract,year,authors.name,externalIds,openAccessPdf,url",
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{BASE_URL}/paper/search", params=params, headers=self._headers()
                )
                response.raise_for_status()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Semantic Scholar search failed: %s", exc)
                return []
        data = response.json()
        papers = data.get("data", [])
        return [self._to_metadata(item) for item in papers if item]

    async def fetch_citations(
        self, paper_id: str, limit: int = 5
    ) -> List[PaperMetadata]:
        url = f"{BASE_URL}/paper/{paper_id}/citations"
        params = {
            "fields": "citingPaper.title,citingPaper.abstract,citingPaper.year,citingPaper.authors.name,citingPaper.externalIds,citingPaper.openAccessPdf,citingPaper.url",
            "limit": limit,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params, headers=self._headers())
                response.raise_for_status()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Semantic Scholar citations failed: %s", exc)
                return []
        data = response.json().get("data", [])
        results: List[PaperMetadata] = []
        for item in data:
            citing_paper = item.get("citingPaper", {})
            meta = self._to_metadata(citing_paper)
            if meta:
                results.append(meta)
        return results

    def _to_metadata(self, payload: dict) -> Optional[PaperMetadata]:
        if not payload:
            return None
        paper_id = payload.get("paperId") or payload.get("externalIds", {}).get("DOI")
        pdf_link = None
        pdf_obj = payload.get("openAccessPdf") or {}
        if isinstance(pdf_obj, dict):
            pdf_link = pdf_obj.get("url")
        authors = payload.get("authors") or []
        author_names = [a.get("name") for a in authors if a.get("name")]
        return PaperMetadata(
            id=str(paper_id) if paper_id else payload.get("url") or payload.get("paperId", ""),
            title=payload.get("title") or "Untitled",
            abstract=payload.get("abstract"),
            authors=author_names,
            year=payload.get("year"),
            pdf_link=pdf_link,
            keywords=[],
            source="semantic_scholar",
        )
