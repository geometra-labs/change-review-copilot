"use client";

import { Line, OrbitControls, Text } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";

type ViewerNode = {
  part_key: string;
  label?: string;
  status: string;
  risk_type?: string;
  box?: {
    position: [number, number, number];
    dimensions: [number, number, number];
  };
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

function BoxNode({
  node,
  selected,
  onClick,
}: {
  node: ViewerNode;
  selected: boolean;
  onClick: () => void;
}) {
  const position = node.box?.position ?? [0, 0, 0];
  const dimensions = node.box?.dimensions ?? [10, 10, 10];

  return (
    <group>
      <mesh
        position={position}
        onClick={(event) => {
          event.stopPropagation();
          onClick();
        }}
      >
        <boxGeometry args={dimensions} />
        <meshStandardMaterial color={selected ? "black" : colorForStatus(node.status)} wireframe={false} />
      </mesh>
      <Text position={[position[0], position[1] + dimensions[1] / 2 + 3, position[2]]} fontSize={2} color="black">
        {node.label ?? node.part_key}
      </Text>
    </group>
  );
}

export default function SimpleAssemblyViewer({
  nodes,
  edges = [],
  selectedPartKey,
  onSelectPart,
}: Props) {
  const nodeMap = Object.fromEntries(nodes.map((node) => [node.part_key, node]));

  return (
    <div style={{ border: "1px solid #ddd", padding: 16, borderRadius: 8 }}>
      <h3>3D Viewer Scaffold</h3>
      <p>Boxes represent parsed part envelopes. Relationship lines show inferred or reported links.</p>

      <div style={{ height: 460, border: "1px solid #ddd", borderRadius: 8, overflow: "hidden", marginBottom: 16 }}>
        <Canvas camera={{ position: [80, 80, 80], fov: 50 }}>
          <ambientLight intensity={0.8} />
          <directionalLight position={[50, 50, 50]} intensity={1.0} />
          <gridHelper args={[200, 20]} />
          {edges.map((edge, index) => {
            const source = nodeMap[edge.source];
            const target = nodeMap[edge.target];
            if (!source?.box || !target?.box) {
              return null;
            }

            return (
              <Line
                key={`${edge.source}-${edge.target}-${edge.relationship_type}-${index}`}
                points={[source.box.position, target.box.position]}
                color={edge.uncertain ? "purple" : "black"}
                lineWidth={1}
              />
            );
          })}
          {nodes.map((node) => (
            <BoxNode
              key={node.part_key}
              node={node}
              selected={selectedPartKey === node.part_key}
              onClick={() => onSelectPart?.(node.part_key)}
            />
          ))}
          <OrbitControls />
        </Canvas>
      </div>

      {edges.length > 0 ? (
        <div style={{ marginBottom: 16 }}>
          <strong>Relationships</strong>
          <ul>
            {edges.slice(0, 20).map((edge, index) => (
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
