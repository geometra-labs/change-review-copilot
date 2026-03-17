"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ChangeEventForm } from "@/components/ChangeEventForm";
import { api } from "@/lib/api";

export default function ChangesPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [assemblies, setAssemblies] = useState<{ id: string; name: string; source: string }[]>([]);
  const [selectedAssemblyId, setSelectedAssemblyId] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.assemblies
      .list(projectId)
      .then((r) => {
        setAssemblies(r.assemblies);
        setSelectedAssemblyId(r.assemblies[0]?.id ?? "");
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) return <p>Loading…</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <main>
      <h1>New change event</h1>
      <p>
        <Link href={`/projects/${projectId}`}>← Project</Link>
      </p>
      {assemblies.length === 0 ? (
        <p>Add an assembly first, then create a change event.</p>
      ) : (
        <>
          <div style={{ marginTop: "1rem" }}>
            <label htmlFor="assembly">Assembly</label>
            <br />
            <select
              id="assembly"
              value={selectedAssemblyId}
              onChange={(e) => setSelectedAssemblyId(e.target.value)}
              style={{ padding: "0.5rem", marginTop: "0.25rem" }}
            >
              {assemblies.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
          <div style={{ marginTop: "1.5rem" }}>
            <ChangeEventForm
              projectId={projectId}
              assemblyId={selectedAssemblyId}
              onSuccess={() => router.push(`/projects/${projectId}/report`)}
            />
          </div>
        </>
      )}
    </main>
  );
}
