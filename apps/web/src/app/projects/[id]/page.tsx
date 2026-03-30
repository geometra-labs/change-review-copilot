"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

type ProjectDetail = {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
  model_versions: Array<{
    id: string;
    label: string;
    source_type: string;
    parse_status: string;
    parse_error?: string | null;
    created_at: string;
  }>;
  comparisons: Array<{
    id: string;
    before_model_version_id: string;
    after_model_version_id: string;
    status: string;
    summary_json: Record<string, unknown>;
    created_at: string;
  }>;
};

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) {
      return;
    }

    apiFetch<ProjectDetail>(`/projects/${projectId}`)
      .then(setProject)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load project"));
  }, [projectId]);

  if (error) {
    return (
      <main style={{ padding: 24 }}>
        <p style={{ color: "crimson" }}>{error}</p>
      </main>
    );
  }

  if (!project) {
    return (
      <main style={{ padding: 24 }}>
        <p>Loading project...</p>
      </main>
    );
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>{project.name}</h1>
      <p>{project.description}</p>

      <p>
        <Link href={`/projects/${project.id}/upload`}>Upload before / after versions</Link>
      </p>

      <section style={{ marginTop: 24 }}>
        <h2>Model Versions</h2>
        {project.model_versions.length === 0 ? (
          <p>No model versions yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Label</th>
                <th>Source</th>
                <th>Status</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {project.model_versions.map((modelVersion) => (
                <tr key={modelVersion.id}>
                  <td>{modelVersion.label}</td>
                  <td>{modelVersion.source_type}</td>
                  <td>{modelVersion.parse_status}</td>
                  <td>{modelVersion.parse_error ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      <section style={{ marginTop: 24 }}>
        <h2>Comparisons</h2>
        {project.comparisons.length === 0 ? (
          <p>No comparisons yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Status</th>
                <th>Summary</th>
                <th>Open</th>
              </tr>
            </thead>
            <tbody>
              {project.comparisons.map((comparison) => (
                <tr key={comparison.id}>
                  <td>{comparison.id}</td>
                  <td>{comparison.status}</td>
                  <td>{JSON.stringify(comparison.summary_json)}</td>
                  <td>
                    <Link href={`/projects/${project.id}/compare/${comparison.id}`}>View Report</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
