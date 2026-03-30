"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

export default function NewProjectPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const project = await api.projects.create({
        name: name.trim(),
        description: description.trim() || undefined,
      });
      router.push(`/projects/${project.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <h1>New project</h1>
        <form onSubmit={onSubmit} style={{ marginTop: "1rem" }}>
          <div>
            <label htmlFor="name">Name</label>
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
            <label htmlFor="description">Description</label>
            <br />
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={loading}
              rows={4}
              style={{ padding: "0.5rem", width: "24rem", marginTop: "0.25rem" }}
            />
          </div>
          {error && <p style={{ color: "red" }}>{error}</p>}
          <button type="submit" disabled={loading} style={{ marginTop: "1rem", padding: "0.5rem 1rem" }}>
            {loading ? "Creating..." : "Create"}
          </button>
        </form>
      </div>
    </AppShell>
  );
}
