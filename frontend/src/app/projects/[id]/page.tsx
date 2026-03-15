"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

export default function ProjectDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [project, setProject] = useState<{
    id: string;
    name: string;
    created_at: string;
    assemblies?: { id: string; name: string; source: string }[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.projects
      .get(id)
      .then(setProject)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <p>Loading…</p>;
  if (error || !project) return <p style={{ color: "red" }}>{error || "Not found"}</p>;

  const assemblies = project.assemblies || [];

  return (
    <main>
      <h1>{project.name}</h1>
      <p>
        <Link href="/projects">← Projects</Link>
      </p>
      <p>
        <Link href={`/projects/${id}/assembly`}>Add assembly</Link>
        {" · "}
        <Link href={`/projects/${id}/changes`}>New change</Link>
        {" · "}
        <Link href={`/projects/${id}/report`}>View report</Link>
      </p>
      <h2>Assemblies</h2>
      {assemblies.length === 0 ? (
        <p>No assemblies. Add one to record changes and generate impact reports.</p>
      ) : (
        <ul>
          {assemblies.map((a) => (
            <li key={a.id}>
              {a.name} ({a.source})
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
