"use client";

type Props = {
  status: string;
};

function bg(status: string): string {
  switch (status) {
    case "completed":
      return "#16a34a";
    case "running":
      return "#2563eb";
    case "queued":
    case "uploaded":
      return "#6b7280";
    case "failed":
    case "high":
      return "#dc2626";
    case "medium":
      return "#ea580c";
    case "low":
      return "#ca8a04";
    case "json":
      return "#0f766e";
    case "html":
      return "#7c3aed";
    case "pdf":
      return "#b91c1c";
    default:
      return "#52525b";
  }
}

export default function StatusBadge({ status }: Props) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "4px 8px",
        borderRadius: 9999,
        background: bg(status),
        color: "white",
        fontSize: 12,
        fontWeight: 600,
      }}
    >
      {status}
    </span>
  );
}
