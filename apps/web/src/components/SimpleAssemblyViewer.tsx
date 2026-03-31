"use client";

type ViewerNode = {
  part_key: string;
  status: string;
  risk_type?: string;
};

type Props = {
  nodes: ViewerNode[];
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

export default function SimpleAssemblyViewer({ nodes }: Props) {
  return (
    <div style={{ border: "1px solid #ddd", padding: 16, borderRadius: 8 }}>
      <h3>Simplified Viewer</h3>
      <p>This is a viewer scaffold. Replace with real 3D geometry rendering later.</p>
      <div style={{ display: "grid", gap: 8 }}>
        {nodes.map((node) => (
          <div
            key={node.part_key}
            style={{
              padding: 8,
              borderRadius: 6,
              background: colorForStatus(node.status),
              color: "white",
            }}
          >
            <strong>{node.part_key}</strong> {node.status}
            {node.risk_type ? ` (${node.risk_type})` : ""}
          </div>
        ))}
      </div>
    </div>
  );
}
