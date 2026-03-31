"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import AppShell from "@/components/AppShell";
import DeleteButton from "@/components/DeleteButton";
import StatusBadge from "@/components/StatusBadge";
import { getToken } from "@/lib/auth";
import { apiFetch } from "@/lib/api";

type Artifact = {
  id: string;
  artifact_type: string;
  uri: string;
  created_at: string;
};

export default function ArtifactsPage() {
  const params = useParams();
  const projectId = params.id as string;
  const comparisonId = params.comparisonId as string;
  const [items, setItems] = useState<Artifact[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadArtifacts(targetComparisonId: string) {
    const data = await apiFetch<{ items: Artifact[] }>(`/comparisons/${targetComparisonId}/artifacts`);
    setItems(data.items);
  }

  useEffect(() => {
    if (!comparisonId) {
      return;
    }

    loadArtifacts(comparisonId)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load artifacts"));
  }, [comparisonId]);

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <p>
          <Link href={`/projects/${projectId}/compare/${comparisonId}`}>Back to Report</Link>
        </p>

        <h1>Artifacts</h1>

        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

        {items.length === 0 ? (
          <p>No exported artifacts yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Created</th>
                <th>Download</th>
                <th>Delete</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td><StatusBadge status={item.artifact_type} /></td>
                  <td>{item.created_at}</td>
                  <td>
                    <button
                      onClick={async () => {
                        try {
                          const token = getToken();
                          const res = await fetch(
                            `${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}/artifacts/${item.id}/download`,
                            {
                              headers: token ? { Authorization: `Bearer ${token}` } : undefined,
                            }
                          );
                          if (!res.ok) {
                            throw new Error(await res.text());
                          }
                          const blob = await res.blob();
                          const url = window.URL.createObjectURL(blob);
                          const anchor = document.createElement("a");
                          anchor.href = url;
                          anchor.download = `artifact_${item.id}.${item.artifact_type}`;
                          anchor.click();
                          window.URL.revokeObjectURL(url);
                        } catch (err) {
                          setError(err instanceof Error ? err.message : "Failed to download artifact");
                        }
                      }}
                    >
                      Download
                    </button>
                  </td>
                  <td>
                    <DeleteButton
                      onDelete={async () => {
                        await apiFetch(`/artifacts/${item.id}`, { method: "DELETE" });
                        await loadArtifacts(comparisonId);
                      }}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </AppShell>
  );
}
