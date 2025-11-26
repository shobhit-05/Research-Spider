import logging
from typing import List, Optional

import httpx

from .config import get_settings
from .models import PaperMetadata

logger = logging.getLogger(__name__)

CLAUDE_URL = "https://api.anthropic.com/v1/messages"


async def call_claude(
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 400,
) -> str:
    settings = get_settings()
    if not settings.anthropic_api_key:
        return (
            "Claude API key missing. Provide ANTHROPIC_API_KEY to enable AI reasoning. "
            "For now, this is a stubbed response."
        )

    headers = {
        "x-api-key": settings.anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        payload["system"] = system

    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            response = await client.post(CLAUDE_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("content", [])
            if isinstance(content, list) and content:
                text_blocks = [block.get("text", "") for block in content if block.get("type") == "text"]
                return "\n".join([t for t in text_blocks if t])
            return data.get("content", "") or "Claude returned an empty response."
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Claude API call failed: %s", exc)
            return "Claude is unavailable at the moment. Please try again later."


async def build_plan_summary(plan_text: str) -> PaperMetadata:
    system_prompt = (
        "You are a research assistant that rewrites a user's research plan into "
        "concise pseudo-paper metadata. Extract keywords, key topics, goals, and a short abstract."
    )
    prompt = (
        "User research plan:\n"
        f"{plan_text}\n\n"
        "Return a summary with title, abstract, keywords, and main authors or stakeholders."
    )
    response = await call_claude(prompt, system=system_prompt, max_tokens=300)
    # Minimal parsing to avoid relying on Claude formatting; this can be replaced by a structured call.
    lines = [line.strip() for line in response.splitlines() if line.strip()]
    keywords: List[str] = []
    title = "User Research Plan"
    abstract_lines: List[str] = []
    authors: List[str] = ["User"]
    for line in lines:
        lowered = line.lower()
        if lowered.startswith("title"):
            title = line.split(":", 1)[-1].strip() or title
        elif lowered.startswith("keyword"):
            kw_part = line.split(":", 1)[-1].strip()
            keywords.extend([kw.strip() for kw in kw_part.split(",") if kw.strip()])
        elif lowered.startswith("author"):
            authors_part = line.split(":", 1)[-1].strip()
            authors = [a.strip() for a in authors_part.split(",") if a.strip()] or authors
        else:
            abstract_lines.append(line)
    abstract = " ".join(abstract_lines) or response
    return PaperMetadata(
        id="user_plan",
        title=title or "User Research Plan",
        abstract=abstract,
        keywords=list(dict.fromkeys(keywords)) if keywords else [],
        authors=authors,
        references=[],
        source="claude",
    )


async def answer_about_paper(
    paper: PaperMetadata, related: List[PaperMetadata], message: str
) -> str:
    related_summaries = "\n".join(
        [f"- {p.title} ({p.year or 'n/a'}) by {', '.join(p.authors[:3])}" for p in related]
    )
    prompt = (
        f"Paper: {paper.title}\n"
        f"Authors: {', '.join(paper.authors)}\n"
        f"Abstract: {paper.abstract or 'N/A'}\n"
        f"Keywords: {', '.join(paper.keywords) if paper.keywords else 'n/a'}\n\n"
        f"Related papers:\n{related_summaries or 'None listed.'}\n\n"
        f"User question: {message}\n"
        "Provide a concise, helpful answer focused on the research details and connections."
    )
    return await call_claude(prompt, max_tokens=400)
