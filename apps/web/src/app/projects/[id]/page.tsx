"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import AppShell from "@/components/AppShell";
import DeleteButton from "@/components/DeleteButton";
import StatusBadge from "@/components/StatusBadge";
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
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadProject(id: string) {
    const data = await apiFetch<ProjectDetail>(`/projects/${id}`);
    setProject(data);
  }

  useEffect(() => {
    if (!projectId) {
      return;
    }

    loadProject(projectId)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load project"));
  }, [projectId]);

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
        {!project ? (
          <p>Loading project...</p>
        ) : (
          <>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h1>{project.name}</h1>
                <p>{project.description}</p>
              </div>
              <DeleteButton
                label="Delete Project"
                onDelete={async () => {
                  await apiFetch(`/projects/${project.id}`, { method: "DELETE" });
                  router.push("/projects");
                }}
              />
            </div>

            <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
              <Link href={`/projects/${project.id}/upload`}>Upload versions</Link>
              <Link href={`/projects/${project.id}/compare/new`}>Compare existing versions</Link>
            </div>

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
                      <th>Open</th>
                      <th>Delete</th>
                    </tr>
                  </thead>
                  <tbody>
                    {project.model_versions.map((modelVersion) => (
                      <tr key={modelVersion.id}>
                        <td>{modelVersion.label}</td>
                        <td>{modelVersion.source_type}</td>
                        <td><StatusBadge status={modelVersion.parse_status} /></td>
                        <td>{modelVersion.parse_error ?? "-"}</td>
                        <td>
                          <Link href={`/projects/${project.id}/models/${modelVersion.id}`}>View</Link>
                        </td>
                        <td>
                          <DeleteButton
                            onDelete={async () => {
                              await apiFetch(`/model-versions/${modelVersion.id}`, { method: "DELETE" });
                              await loadProject(project.id);
                            }}
                          />
                        </td>
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
                        <td><StatusBadge status={comparison.status} /></td>
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
          </>
        )}
      </div>
    </AppShell>
  );
}
