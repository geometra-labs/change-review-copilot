"use client";

import { FormEvent, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import AppShell from "@/components/AppShell";
import { getToken } from "@/lib/auth";
import { apiFetch } from "@/lib/api";
import { pollUntil } from "@/lib/poll";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type JobResponse = {
  id: string;
  job_type: string;
  resource_type: string;
  resource_id: string;
  status: string;
  error_message: string | null;
  metadata_json: Record<string, unknown>;
};

type ModelVersionResponse = {
  id: string;
  parse_status: string;
  parse_error?: string | null;
};

export default function UploadPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;
  const [beforeFile, setBeforeFile] = useState<File | null>(null);
  const [afterFile, setAfterFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyText, setBusyText] = useState<string | null>(null);

  async function uploadVersion(label: string, file: File) {
    const token = getToken();
    const form = new FormData();
    form.append("label", label);
    form.append("source_type", "normalized_json");
    form.append("file", file);

    const res = await fetch(`${API_BASE}/projects/${projectId}/model-versions`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      body: form,
    });
    if (!res.ok) {
      throw new Error(await res.text());
    }
    return res.json();
  }

  async function parseVersion(modelVersionId: string) {
    return apiFetch<{ job_id: string; status: string }>(`/model-versions/${modelVersionId}/parse`, {
      method: "POST",
    });
  }

  async function getModelVersion(modelVersionId: string) {
    return apiFetch<ModelVersionResponse>(`/model-versions/${modelVersionId}`);
  }

  async function getJob(jobId: string) {
    return apiFetch<JobResponse>(`/jobs/${jobId}`);
  }

  async function createComparison(beforeId: string, afterId: string) {
    return apiFetch<{ id: string; job_id: string; status: string }>(`/projects/${projectId}/comparisons`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        before_model_version_id: beforeId,
        after_model_version_id: afterId,
      }),
    });
  }

  async function waitForJob(jobId: string) {
    const job = await pollUntil(
      () => getJob(jobId),
      (value) => value.status === "completed" || value.status === "failed"
    );

    if (job.status === "failed") {
      throw new Error(job.error_message || "Job failed");
    }

    return job;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!beforeFile || !afterFile || !projectId) {
      setError("Project and both files are required");
      return;
    }

    try {
      setBusyText("Uploading files...");
      const before = await uploadVersion("before", beforeFile);
      const after = await uploadVersion("after", afterFile);

      setBusyText("Parsing before version...");
      const beforeParse = await parseVersion(before.id);
      await waitForJob(beforeParse.job_id);
      const beforeStatus = await getModelVersion(before.id);
      if (beforeStatus.parse_status !== "completed") {
        throw new Error(beforeStatus.parse_error || "Before version parse failed");
      }

      setBusyText("Parsing after version...");
      const afterParse = await parseVersion(after.id);
      await waitForJob(afterParse.job_id);
      const afterStatus = await getModelVersion(after.id);
      if (afterStatus.parse_status !== "completed") {
        throw new Error(afterStatus.parse_error || "After version parse failed");
      }

      setBusyText("Creating comparison...");
      const comparison = await createComparison(before.id, after.id);
      await waitForJob(comparison.job_id);

      setBusyText(null);
      router.push(`/projects/${projectId}/compare/${comparison.id}`);
    } catch (err) {
      setBusyText(null);
      setError(err instanceof Error ? err.message : "Upload flow failed");
    }
  }

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <h1>Upload Before / After Models</h1>
        <form onSubmit={onSubmit} style={{ display: "grid", gap: 12, maxWidth: 480 }}>
          <label>
            Before file
            <input type="file" accept=".json" onChange={(e) => setBeforeFile(e.target.files?.[0] ?? null)} />
          </label>
          <label>
            After file
            <input type="file" accept=".json" onChange={(e) => setAfterFile(e.target.files?.[0] ?? null)} />
          </label>
          <button type="submit" disabled={Boolean(busyText)}>
            {busyText ?? "Upload and Compare"}
          </button>
        </form>

        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
      </div>
    </AppShell>
  );
}
