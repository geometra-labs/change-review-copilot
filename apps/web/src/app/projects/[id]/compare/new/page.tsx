"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import AppShell from "@/components/AppShell";
import { apiFetch } from "@/lib/api";
import { pollUntil } from "@/lib/poll";

type ProjectDetail = {
  id: string;
  name: string;
  model_versions: Array<{
    id: string;
    label: string;
    parse_status: string;
    created_at: string;
  }>;
};

type JobResponse = {
  id: string;
  status: string;
  error_message: string | null;
};

export default function NewComparisonPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [beforeId, setBeforeId] = useState("");
  const [afterId, setAfterId] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) {
      return;
    }

    apiFetch<ProjectDetail>(`/projects/${projectId}`)
      .then((data) => {
        setProject(data);
        const completed = data.model_versions.filter((modelVersion) => modelVersion.parse_status === "completed");
        if (completed.length >= 2) {
          setBeforeId(completed[1].id);
          setAfterId(completed[0].id);
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load versions"));
  }, [projectId]);

  async function waitForJob(jobId: string) {
    const job = await pollUntil(
      () => apiFetch<JobResponse>(`/jobs/${jobId}`),
      (value) => value.status === "completed" || value.status === "failed"
    );

    if (job.status === "failed") {
      throw new Error(job.error_message || "Comparison failed");
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!beforeId || !afterId) {
      setError("Select both before and after versions");
      return;
    }
    if (beforeId === afterId) {
      setError("Before and after versions must be different");
      return;
    }

    try {
      setBusy("Creating comparison...");
      const comparison = await apiFetch<{ id: string; job_id: string }>(`/projects/${projectId}/comparisons`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          before_model_version_id: beforeId,
          after_model_version_id: afterId,
        }),
      });

      await waitForJob(comparison.job_id);

      setBusy(null);
      router.push(`/projects/${projectId}/compare/${comparison.id}`);
    } catch (err) {
      setBusy(null);
      setError(err instanceof Error ? err.message : "Failed to create comparison");
    }
  }

  const completedVersions = project?.model_versions.filter((modelVersion) => modelVersion.parse_status === "completed") ?? [];

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <h1>Create Comparison from Existing Versions</h1>

        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

        {!project ? (
          <p>Loading project...</p>
        ) : completedVersions.length < 2 ? (
          <p>You need at least two parsed versions before creating a comparison.</p>
        ) : (
          <form onSubmit={onSubmit} style={{ display: "grid", gap: 12, maxWidth: 480 }}>
            <label>
              Before version
              <select value={beforeId} onChange={(e) => setBeforeId(e.target.value)}>
                {completedVersions.map((modelVersion) => (
                  <option key={modelVersion.id} value={modelVersion.id}>
                    {modelVersion.label} ({modelVersion.created_at})
                  </option>
                ))}
              </select>
            </label>

            <label>
              After version
              <select value={afterId} onChange={(e) => setAfterId(e.target.value)}>
                {completedVersions.map((modelVersion) => (
                  <option key={modelVersion.id} value={modelVersion.id}>
                    {modelVersion.label} ({modelVersion.created_at})
                  </option>
                ))}
              </select>
            </label>

            <button type="submit" disabled={Boolean(busy)}>
              {busy ?? "Create Comparison"}
            </button>
          </form>
        )}
      </div>
    </AppShell>
  );
}
