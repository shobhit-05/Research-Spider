import { useEffect, useRef } from "react";
import { DataSet, Network, NodeOptions, EdgeOptions } from "vis-network/standalone";
import { GraphEdge, GraphNode } from "../types";

interface Props {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onSelect: (nodeId: string | null) => void;
}

const edgeColors: Record<GraphEdge["type"], string> = {
  citation: "#f97316",
  semantic: "#22d3ee",
  keyword: "#a855f7",
  author: "#facc15",
};

export default function GraphCanvas({ nodes, edges, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const networkRef = useRef<Network | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const dataNodes = new DataSet<NodeOptions>(
      nodes.map((n) => ({
        id: n.id,
        label: n.title,
        color: {
          background: "#0ea5e9",
          border: "#22d3ee",
          highlight: { background: "#f97316", border: "#f97316" },
        },
        font: { color: "#e2e8f0", size: 14 },
        shape: "dot",
        size: Math.min(30, 10 + (n.keywords?.length || 0) * 2),
      }))
    );

    const dataEdges = new DataSet<EdgeOptions>(
      edges.map((e) => ({
        from: e.source,
        to: e.target,
        color: { color: edgeColors[e.type] || "#a0aec0" },
        width: 2,
        arrows: "to",
        smooth: true,
      }))
    );

    const options = {
      physics: {
        enabled: true,
        stabilization: false,
      },
      interaction: {
        hover: true,
        zoomView: true,
        dragView: true,
      },
      layout: {
        improvedLayout: true,
      },
    };

    if (networkRef.current) {
      networkRef.current.setData({ nodes: dataNodes, edges: dataEdges });
    } else {
      networkRef.current = new Network(containerRef.current, { nodes: dataNodes, edges: dataEdges }, options);
      networkRef.current.on("selectNode", (params) => {
        const nodeId = params?.nodes?.[0];
        onSelect(nodeId ?? null);
      });
      networkRef.current.on("deselectNode", () => onSelect(null));
    }
  }, [nodes, edges, onSelect]);

  return <div ref={containerRef} className="w-full h-[500px] rounded-xl glass" />;
}
