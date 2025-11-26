from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class InputType(str, Enum):
    research_plan = "research_plan"
    paper_link = "paper_link"


class PaperMetadata(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique identifier from source")
    title: str
    abstract: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    pdf_link: Optional[HttpUrl] = None
    source: Optional[str] = None
    references: List[str] = Field(default_factory=list)


class AnalyzeInputRequest(BaseModel):
    input_text: str


class AnalyzeInputResponse(BaseModel):
    input_type: InputType
    metadata: PaperMetadata


class GraphNode(PaperMetadata):
    id: str


class EdgeType(str, Enum):
    citation = "citation"
    semantic = "semantic"
    keyword = "keyword"
    author = "author"


class GraphEdge(BaseModel):
    source: str
    target: str
    type: EdgeType


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class ExpandGraphRequest(BaseModel):
    root_metadata: PaperMetadata
    max_nodes: int = Field(default=30, ge=1, le=100)
    max_depth: int = Field(default=2, ge=1, le=5)


class ClaudeChatRequest(BaseModel):
    paper_metadata: PaperMetadata
    related_papers: List[PaperMetadata] = Field(default_factory=list)
    message: str


class ClaudeChatResponse(BaseModel):
    answer: str
