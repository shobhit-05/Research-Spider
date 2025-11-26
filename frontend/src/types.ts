export type InputType = "research_plan" | "paper_link";

export interface PaperMetadata {
  id?: string;
  title: string;
  abstract?: string;
  keywords: string[];
  authors: string[];
  year?: number;
  pdf_link?: string;
  source?: string;
  references?: string[];
}

export interface GraphNode extends PaperMetadata {
  id: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: "citation" | "semantic" | "keyword" | "author";
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface AnalyzeInputResponse {
  input_type: InputType;
  metadata: PaperMetadata;
}
