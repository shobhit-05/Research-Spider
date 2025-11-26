import { GraphNode } from "../types";

interface Props {
  node: GraphNode | null;
  onExpand: (node: GraphNode) => void;
}

export default function Sidebar({ node, onExpand }: Props) {
  if (!node) {
    return (
      <div className="glass p-4 rounded-xl text-slate-300">
        <p>Select a node to view its details.</p>
      </div>
    );
  }

  return (
    <div className="glass p-4 rounded-xl space-y-3">
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-400">Title</p>
        <h2 className="text-lg font-semibold text-white">{node.title}</h2>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-400">Authors</p>
        <p className="text-sm text-slate-200">{node.authors?.join(", ") || "Unknown"}</p>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-400">Abstract</p>
        <p className="text-sm text-slate-200 line-clamp-6">{node.abstract || "No abstract available."}</p>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-400">Keywords</p>
        <div className="flex flex-wrap gap-2 mt-1">
          {(node.keywords || []).map((kw) => (
            <span
              key={kw}
              className="px-2 py-1 rounded-full bg-slate-800 text-slate-100 text-xs border border-slate-700"
            >
              {kw}
            </span>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-2">
        {node.pdf_link && (
          <a
            href={node.pdf_link}
            target="_blank"
            rel="noreferrer"
            className="text-accent text-sm hover:underline"
          >
            PDF Link
          </a>
        )}
        <button
          className="ml-auto rounded-md bg-accent text-black px-3 py-2 text-sm font-semibold hover:opacity-90"
          onClick={() => onExpand(node)}
        >
          Expand graph from this node
        </button>
      </div>
    </div>
  );
}
