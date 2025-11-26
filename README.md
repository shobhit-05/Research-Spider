Research Spider
================

AI-powered research exploration tool built with FastAPI (backend) and React + Tailwind (frontend). It ingests a research plan or DOI/link, generates pseudo metadata with Claude, queries public research APIs (Semantic Scholar, OpenAlex, arXiv), and builds an interactive research graph in the browser. No database is used; all processing is in-memory.

## Features
- Input a free-form research plan or DOI/paper link.
- Claude-powered plan parsing and Q&A about any selected paper.
- Multi-source paper retrieval (Semantic Scholar, OpenAlex, arXiv).
- Graph expansion engine that explores related papers by citation, author, and semantic cues with depth/size limits.
- React + vis-network graph UI with node details, expansion controls, and chat sidebar.

## Project structure
- `backend/` – FastAPI app, API clients, graph builder, Claude integration.
- `frontend/` – React + Vite + Tailwind UI, graph canvas, chat, and sidebar components.
- `.env.example` – Environment variables for API keys and config.

## Backend (FastAPI)
**Dependencies:** `python3.11+`, `fastapi`, `uvicorn`, `httpx`.

Install:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run:
```bash
# from repo root
uvicorn backend.app.main:app --reload --port 8000
# or from backend directory
# uvicorn app.main:app --reload --port 8000
```

### API endpoints
- `POST /analyze-input` – Detects plan vs DOI/link. Returns `metadata` describing the root paper/plan.
- `POST /expand-graph` – Expands from `root_metadata` with `max_nodes`/`max_depth`, returning `{nodes, edges}` for visualization.
- `POST /claude-chat` – Claude Q&A given `paper_metadata`, optional `related_papers`, and a `message`.

### Environment
Copy `.env.example` to a repo-root `.env` and fill:
- `ANTHROPIC_API_KEY` (required for Claude features; stubbed responses without it)
- `SEMANTIC_SCHOLAR_API_KEY` (optional but recommended)
- `OPENALEX_EMAIL` (recommended for OpenAlex rate limits)
- `REQUEST_TIMEOUT_SECONDS`, `MAX_GRAPH_NODES`, `MAX_GRAPH_DEPTH`

## Frontend (React + Vite + Tailwind)
**Dependencies:** Node 18+.

Install and run:
```bash
cd frontend
npm install
npm run dev   # starts Vite on http://localhost:5173
```

Build:
```bash
npm run build
```

Environment:
- Set `VITE_API_BASE_URL` to your FastAPI server (e.g., `http://localhost:8000`).

## Usage flow
1. Start the backend (FastAPI) and frontend (Vite).
2. Enter a research plan or DOI/link and click **Generate Research Web**.
3. Explore the interactive graph: pan/zoom, select nodes to view details, expand from any node.
4. Use the Claude chat panel to ask about a selected paper and its connections.

## Notes
- All processing is in-memory; no database is used.
- External API calls use graceful fallbacks and timeouts; responses may be partial if an API key is missing.
- Claude endpoints will return stubbed messages when `ANTHROPIC_API_KEY` is not provided.
