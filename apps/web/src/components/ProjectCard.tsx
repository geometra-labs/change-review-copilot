import Link from "next/link";

interface ProjectCardProps {
  id: string;
  name: string;
  created_at: string;
}

export function ProjectCard({ id, name, created_at }: ProjectCardProps) {
  return (
    <div style={{ border: "1px solid #ccc", padding: "1rem", marginBottom: "0.5rem", borderRadius: 4 }}>
      <Link href={`/projects/${id}/upload`} style={{ fontWeight: 600 }}>
        {name}
      </Link>
      <div style={{ fontSize: "0.875rem", color: "#666" }}>{new Date(created_at).toLocaleDateString()}</div>
    </div>
  );
}
