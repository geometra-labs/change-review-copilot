"use client";

import { useState } from "react";

interface AssemblyUploadProps {
  projectId: string;
  onSuccess: () => void;
}

export function AssemblyUpload({ projectId, onSuccess }: AssemblyUploadProps) {
  const [name, setName] = useState("");
  const [source, setSource] = useState<"upload" | "onshape">("upload");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { api } = await import("@/lib/api");
      await api.assemblies.create(projectId, { name: name.trim(), source });
      onSuccess();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to add assembly");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <div>
        <label htmlFor="name">Assembly name</label>
        <br />
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          disabled={loading}
          style={{ padding: "0.5rem", width: "20rem", marginTop: "0.25rem" }}
        />
      </div>
      <div style={{ marginTop: "0.75rem" }}>
        <label>Source</label>
        <br />
        <select
          value={source}
          onChange={(e) => setSource(e.target.value as "upload" | "onshape")}
          disabled={loading}
          style={{ padding: "0.5rem", marginTop: "0.25rem" }}
        >
          <option value="upload">Upload (mock)</option>
          <option value="onshape">Onshape (mock)</option>
        </select>
      </div>
      {error && <p style={{ color: "red", marginTop: "0.5rem" }}>{error}</p>}
      <button type="submit" disabled={loading} style={{ marginTop: "1rem", padding: "0.5rem 1rem" }}>
        {loading ? "Adding…" : "Add assembly"}
      </button>
    </form>
  );
}
