"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { getStoredToken } from "@/lib/auth";
import { api } from "@/lib/api";

type ProjectDetail = {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
  model_versions?: {
    id: string;
    label: string;
    source_type: string;
    parse_status: string;
    created_at: string;
  }[];
};

export default function ProjectDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasToken, setHasToken] = useState(false);

  useEffect(() => {
    const token = getStoredToken();
    setHasToken(Boolean(token));
    if (!token) {
      setLoading(false);
      return;
    }

    api.projects
      .get(id)
      .then(setProject)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [id]);

  if (!hasToken) {
    return (
      <main style={{ padding: 24 }}>
        <h1>Project</h1>
        <p>This page requires login.</p>
        <p>
          <Link href="/login">Login or register</Link>
        </p>
      </main>
    );
  }

  if (loading) return <p>Loading...</p>;
  if (error || !project) return <p style={{ color: "red" }}>{error || "Not found"}</p>;

  const modelVersions = project.model_versions ?? [];

  return (
    <main style={{ padding: 24 }}>
      <h1>{project.name}</h1>
      <p>
        <Link href="/projects">Projects</Link>
      </p>
      {project.description ? <p>{project.description}</p> : null}

      <h2 style={{ marginTop: 24 }}>Model Versions</h2>
      {modelVersions.length === 0 ? (
        <p>No model versions yet. Upload flow is the next UI step to wire.</p>
      ) : (
        <ul>
          {modelVersions.map((modelVersion) => (
            <li key={modelVersion.id}>
              {modelVersion.label} - {modelVersion.source_type} - {modelVersion.parse_status}
            </li>
          ))}
        </ul>
      )}
      <p style={{ marginTop: 24 }}>Comparison and upload UI is the next frontend step to connect.</p>
    </main>
  );
}
