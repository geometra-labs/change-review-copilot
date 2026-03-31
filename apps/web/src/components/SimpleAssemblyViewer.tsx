"use client";

type ViewerNode = {
  part_key: string;
  label?: string;
  status: string;
  risk_type?: string;
};

type ViewerEdge = {
  source: string;
  target: string;
  relationship_type: string;
  uncertain?: boolean;
};

type Props = {
  nodes: ViewerNode[];
  edges?: ViewerEdge[];
  selectedPartKey?: string | null;
  onSelectPart?: (partKey: string) => void;
};

function colorForStatus(status: string): string {
  if (status === "changed") {
    return "#4f46e5";
  }
  if (status === "high") {
    return "#dc2626";
  }
  if (status === "medium") {
    return "#ea580c";
  }
  if (status === "low") {
    return "#ca8a04";
  }
  return "#6b7280";
}

export default function SimpleAssemblyViewer({
  nodes,
  edges = [],
  selectedPartKey,
  onSelectPart,
}: Props) {
  return (
    <div style={{ border: "1px solid #ddd", padding: 16, borderRadius: 8 }}>
      <h3>Interactive Viewer Scaffold</h3>
      <p>This is still a simplified graph-like viewer, but now supports selection and relation display.</p>

      {edges.length > 0 ? (
        <div style={{ marginBottom: 16 }}>
          <strong>Relationships</strong>
          <ul>
            {edges.map((edge, index) => (
              <li key={`${edge.source}-${edge.target}-${edge.relationship_type}-${index}`}>
                {edge.source} {"->"} {edge.target} ({edge.relationship_type}
                {edge.uncertain ? ", uncertain" : ""})
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div style={{ display: "grid", gap: 8 }}>
        {nodes.map((node) => {
          const selected = selectedPartKey === node.part_key;
          return (
            <button
            key={node.part_key}
            onClick={() => onSelectPart?.(node.part_key)}
            style={{
              padding: 10,
              borderRadius: 8,
              border: selected ? "3px solid black" : "1px solid #ddd",
              background: colorForStatus(node.status),
              color: "white",
              textAlign: "left",
              cursor: "pointer",
            }}
          >
            <strong>{node.label ?? node.part_key}</strong>
            <div>{node.part_key}</div>
            <div>{node.status}{node.risk_type ? ` ${node.risk_type}` : ""}</div>
          </button>
          );
        })}
      </div>
    </div>
  );
}
