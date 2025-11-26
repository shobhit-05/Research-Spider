import { AnalyzeInputResponse, GraphResponse, PaperMetadata } from "./types";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Request failed");
  }
  return response.json();
}

export async function analyzeInput(input_text: string): Promise<AnalyzeInputResponse> {
  return request<AnalyzeInputResponse>("/analyze-input", {
    method: "POST",
    body: JSON.stringify({ input_text }),
  });
}

export async function expandGraph(
  root_metadata: PaperMetadata,
  max_nodes: number,
  max_depth: number
): Promise<GraphResponse> {
  return request<GraphResponse>("/expand-graph", {
    method: "POST",
    body: JSON.stringify({ root_metadata, max_nodes, max_depth }),
  });
}

export async function claudeChat(
  paper_metadata: PaperMetadata,
  related_papers: PaperMetadata[],
  message: string
): Promise<{ answer: string }> {
  return request<{ answer: string }>("/claude-chat", {
    method: "POST",
    body: JSON.stringify({ paper_metadata, related_papers, message }),
  });
}
