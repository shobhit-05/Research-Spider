import { useMemo, useState } from "react";
import { analyzeInput, expandGraph } from "./api";
import InputForm from "./components/InputForm";
import GraphCanvas from "./components/GraphCanvas";
import Sidebar from "./components/Sidebar";
import ChatPanel from "./components/ChatPanel";
import { GraphNode, GraphResponse, PaperMetadata } from "./types";

function Hero() {
  return (
    <div className="space-y-2">
      <p className="uppercase text-xs tracking-[0.3em] text-teal">Research Spider</p>
      <h1 className="text-3xl md:text-4xl font-bold text-white">
        Spin a web of related research in seconds.
      </h1>
      <p className="text-slate-300 max-w-2xl">
        Start with a research plan or a DOI/link. Research Spider pulls related papers,
        authors, and concepts, then visualizes the graph so you can explore and chat with
        Claude about each node.
      </p>
    </div>
  );
}

export default function App() {
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [limits] = useState({ maxNodes: 30, maxDepth: 2 });
  const selectedNode = useMemo<GraphNode | null>(() => {
    if (!graph || !selectedId) return null;
    return graph.nodes.find((n) => n.id === selectedId) || null;
  }, [graph, selectedId]);

  const relatedForChat: PaperMetadata[] = useMemo(() => {
    if (!graph || !selectedNode) return [];
    return graph.nodes.filter((n) => n.id !== selectedNode.id).slice(0, 10);
  }, [graph, selectedNode]);

  const handleGenerate = async (input: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const analyzed = await analyzeInput(input);
      const expanded = await expandGraph(
        analyzed.metadata,
        limits.maxNodes,
        limits.maxDepth
      );
      setGraph(expanded);
      setSelectedId(analyzed.metadata.id || expanded.nodes[0]?.id || null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to generate graph";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const expandFromNode = async (node: GraphNode) => {
    setIsLoading(true);
    setError(null);
    try {
      const expanded = await expandGraph(node, limits.maxNodes, limits.maxDepth);
      setGraph(expanded);
      setSelectedId(node.id);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to expand graph";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
        <Hero />
        <InputForm onSubmit={handleGenerate} isLoading={isLoading} />
        {error && (
          <div className="glass p-3 rounded-lg text-red-300 border border-red-500/40">
            {error}
          </div>
        )}
        {graph && (
          <div className="grid md:grid-cols-3 gap-4 items-start">
            <div className="md:col-span-2 space-y-3">
              <GraphCanvas
                nodes={graph.nodes}
                edges={graph.edges}
                onSelect={setSelectedId}
              />
            </div>
            <div className="space-y-3">
              <Sidebar node={selectedNode} onExpand={expandFromNode} />
              <ChatPanel selected={selectedNode} related={relatedForChat} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
