"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import AppShell from "@/components/AppShell";
import { apiFetch } from "@/lib/api";

type ModelVersion = {
  id: string;
  project_id: string;
  label: string;
  source_type: string;
  file_uri: string;
  parse_status: string;
  parse_error?: string | null;
  created_at: string;
};

type PartsResponse = {
  items: Array<{
    id: string;
    part_key: string;
    name: string;
    parent_part_key?: string | null;
    geometry_signature?: string | null;
  }>;
};

export default function ModelVersionDetailPage() {
  const params = useParams();
  const projectId = params.id as string;
  const modelVersionId = params.modelVersionId as string;
  const [modelVersion, setModelVersion] = useState<ModelVersion | null>(null);
  const [parts, setParts] = useState<PartsResponse["items"]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!modelVersionId) {
      return;
    }

    Promise.all([
      apiFetch<ModelVersion>(`/model-versions/${modelVersionId}`),
      apiFetch<PartsResponse>(`/model-versions/${modelVersionId}/parts`).catch(() => ({ items: [] })),
    ])
      .then(([modelVersionValue, partsRes]) => {
        setModelVersion(modelVersionValue);
        setParts(partsRes.items);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load model version"));
  }, [modelVersionId]);

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <p>
          <Link href={`/projects/${projectId}`}>Back to Project</Link>
        </p>

        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

        {!modelVersion ? (
          <p>Loading model version...</p>
        ) : (
          <>
            <h1>Model Version: {modelVersion.label}</h1>
            <p>Status: {modelVersion.parse_status}</p>
            <p>Source: {modelVersion.source_type}</p>
            <p>Error: {modelVersion.parse_error ?? "-"}</p>

            <section style={{ marginTop: 24 }}>
              <h2>Parts</h2>
              {parts.length === 0 ? (
                <p>No parts found.</p>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Part Key</th>
                      <th>Name</th>
                      <th>Parent</th>
                      <th>Geometry Signature</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parts.map((part) => (
                      <tr key={part.id}>
                        <td>{part.part_key}</td>
                        <td>{part.name}</td>
                        <td>{part.parent_part_key ?? "-"}</td>
                        <td>{part.geometry_signature ?? "-"}</td>
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
