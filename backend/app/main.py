import logging
import re
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .claude import answer_about_paper, build_plan_summary
from .clients.semantic_scholar import SemanticScholarClient
from .clients.openalex import OpenAlexClient
from .config import Settings, get_settings
from .graph_engine import GraphBuilder
from .models import (
    AnalyzeInputRequest,
    AnalyzeInputResponse,
    ClaudeChatRequest,
    ClaudeChatResponse,
    ExpandGraphRequest,
    GraphResponse,
    InputType,
    PaperMetadata,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Research Spider")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def detect_input_type(text: str) -> InputType:
    if re.search(r"10\\.\\d{4,9}/[-._;()/:A-Z0-9]+", text, re.IGNORECASE) or text.startswith(
        "http"
    ):
        return InputType.paper_link
    return InputType.research_plan


def get_semantic_client(settings: Settings = Depends(get_settings)) -> SemanticScholarClient:
    return SemanticScholarClient(api_key=settings.semantic_scholar_api_key)


def get_openalex_client(settings: Settings = Depends(get_settings)) -> OpenAlexClient:
    return OpenAlexClient(email=settings.openalex_email)


@app.post("/analyze-input", response_model=AnalyzeInputResponse)
async def analyze_input(
    payload: AnalyzeInputRequest,
    semantic_client: SemanticScholarClient = Depends(get_semantic_client),
    openalex_client: OpenAlexClient = Depends(get_openalex_client),
) -> AnalyzeInputResponse:
    text = payload.input_text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text is required.")

    input_type = detect_input_type(text)
    metadata: Optional[PaperMetadata] = None

    if input_type == InputType.research_plan:
        metadata = await build_plan_summary(text)
    else:
        doi_match = re.search(r"10\\.\\d{4,9}/[-._;()/:A-Z0-9]+", text, re.IGNORECASE)
        doi = doi_match.group(0) if doi_match else None
        metadata = await semantic_client.fetch_paper(doi or text)
        if not metadata and doi:
            metadata = await openalex_client.fetch_by_doi(doi)
        if not metadata:
            raise HTTPException(status_code=404, detail="Paper could not be retrieved.")
    return AnalyzeInputResponse(input_type=input_type, metadata=metadata)


@app.post("/expand-graph", response_model=GraphResponse)
async def expand_graph(payload: ExpandGraphRequest) -> GraphResponse:
    builder = GraphBuilder()
    return await builder.expand(
        payload.root_metadata, max_nodes=payload.max_nodes, max_depth=payload.max_depth
    )


@app.post("/claude-chat", response_model=ClaudeChatResponse)
async def claude_chat(payload: ClaudeChatRequest) -> ClaudeChatResponse:
    answer = await answer_about_paper(
        payload.paper_metadata, payload.related_papers, payload.message
    )
    return ClaudeChatResponse(answer=answer)
