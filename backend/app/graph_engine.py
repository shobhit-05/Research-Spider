import asyncio
import logging
from collections import deque
from typing import Dict, List, Set, Tuple

from .clients.arxiv import ArxivClient
from .clients.openalex import OpenAlexClient
from .clients.semantic_scholar import SemanticScholarClient
from .models import EdgeType, GraphEdge, GraphNode, GraphResponse, PaperMetadata
from .config import get_settings

logger = logging.getLogger(__name__)


class GraphBuilder:
    def __init__(self) -> None:
        settings = get_settings()
        self.semantic_client = SemanticScholarClient(timeout=settings.request_timeout)
        self.openalex_client = OpenAlexClient(timeout=settings.request_timeout)
        self.arxiv_client = ArxivClient(timeout=settings.request_timeout)
        self.max_nodes = settings.max_graph_nodes
        self.max_depth = settings.max_graph_depth

    async def expand(
        self, root: PaperMetadata, max_nodes: int | None = None, max_depth: int | None = None
    ) -> GraphResponse:
        max_nodes = max_nodes or self.max_nodes
        max_depth = max_depth or self.max_depth
        nodes: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []
        seen: Set[str] = set()

        def add_node(meta: PaperMetadata) -> GraphNode:
            node_id = meta.id or meta.title
            graph_node = GraphNode(**meta.dict(), id=node_id)
            nodes[node_id] = graph_node
            return graph_node

        root_node = add_node(root)
        queue: deque[Tuple[GraphNode, int]] = deque([(root_node, 0)])
        seen.add(root_node.id)

        while queue and len(nodes) < max_nodes:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            related = await self._gather_related(current)
            for meta, edge_type in related:
                node_id = meta.id or meta.title
                if node_id in seen:
                    edges.append(GraphEdge(source=current.id, target=node_id, type=edge_type))
                    continue
                if len(nodes) >= max_nodes:
                    continue
                seen.add(node_id)
                new_node = add_node(meta)
                edges.append(GraphEdge(source=current.id, target=new_node.id, type=edge_type))
                queue.append((new_node, depth + 1))
        return GraphResponse(nodes=list(nodes.values()), edges=edges)

    async def _gather_related(
        self, node: GraphNode
    ) -> List[tuple[PaperMetadata, EdgeType]]:
        keywords = node.keywords or (node.title.split() if node.title else [])
        tasks = [
            self.semantic_client.search_by_keywords(keywords, limit=5),
            self.semantic_client.fetch_citations(node.id, limit=5),
            self.openalex_client.search_by_title(node.title, limit=3),
            self.openalex_client.related_by_authors(node.authors, limit=3),
            self.arxiv_client.search(keywords, limit=3),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        related: List[tuple[PaperMetadata, EdgeType]] = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning("Related search failed: %s", result)
                continue
            edge_type = EdgeType.semantic
            if idx == 1:
                edge_type = EdgeType.citation
            elif idx in (2, 4):
                edge_type = EdgeType.semantic
            elif idx == 3:
                edge_type = EdgeType.author
            for meta in result:
                related.append((meta, edge_type))
        return related
