import logging
from typing import List
from xml.etree import ElementTree

import httpx

from ..config import get_settings
from ..models import PaperMetadata

logger = logging.getLogger(__name__)

BASE_URL = "http://export.arxiv.org/api/query"


class ArxivClient:
    def __init__(self, timeout: int = 15) -> None:
        settings = get_settings()
        self.timeout = timeout or settings.request_timeout

    async def search(self, keywords: List[str], limit: int = 5) -> List[PaperMetadata]:
        if not keywords:
            return []
        query = "+AND+".join(f"all:{kw}" for kw in keywords)
        params = {"search_query": query, "start": 0, "max_results": limit}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(BASE_URL, params=params)
                response.raise_for_status()
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("arXiv search failed: %s", exc)
                return []
        return self._parse_feed(response.text)

    def _parse_feed(self, xml_text: str) -> List[PaperMetadata]:
        results: List[PaperMetadata] = []
        try:
            root = ElementTree.fromstring(xml_text)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("arXiv XML parse failed: %s", exc)
            return results
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            abstract_el = entry.find("atom:summary", ns)
            link_el = entry.find("atom:link[@type='application/pdf']", ns)
            authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns) if a.find("atom:name", ns) is not None]
            paper_id = entry.find("atom:id", ns)
            results.append(
                PaperMetadata(
                    id=paper_id.text if paper_id is not None else "",
                    title=title_el.text.strip() if title_el is not None else "Untitled",
                    abstract=abstract_el.text.strip() if abstract_el is not None else None,
                    authors=authors,
                    year=None,
                    pdf_link=link_el.get("href") if link_el is not None else None,
                    keywords=[],
                    source="arxiv",
                    references=[],
                )
            )
        return results
