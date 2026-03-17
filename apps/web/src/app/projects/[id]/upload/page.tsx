"use client";

import { FormEvent, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { getToken } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function UploadPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;
  const [beforeFile, setBeforeFile] = useState<File | null>(null);
  const [afterFile, setAfterFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

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
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function parseVersion(modelVersionId: string) {
    const token = getToken();
    const res = await fetch(`${API_BASE}/model-versions/${modelVersionId}/parse`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function createComparison(beforeId: string, afterId: string) {
    const token = getToken();
    const res = await fetch(`${API_BASE}/projects/${projectId}/comparisons`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        before_model_version_id: beforeId,
        after_model_version_id: afterId,
      }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!beforeFile || !afterFile || !projectId) {
      setError("Project and both files are required");
      return;
    }

    setBusy(true);
    try {
      const before = await uploadVersion("before", beforeFile);
      const after = await uploadVersion("after", afterFile);

      await parseVersion(before.id);
      await parseVersion(after.id);

      const comparison = await createComparison(before.id, after.id);
      router.push(`/projects/${projectId}/compare/${comparison.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload flow failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ padding: 24 }}>
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
        <button type="submit" disabled={busy}>
          {busy ? "Running..." : "Upload and Compare"}
        </button>
      </form>

      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}
    </main>
  );
}
