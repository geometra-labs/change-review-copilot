"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

import { apiFetch } from "@/lib/api";

type Project = {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
};

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("Demo Working Project");
  const [description, setDescription] = useState("My first project");
  const [error, setError] = useState<string | null>(null);

  async function loadProjects() {
    try {
      const data = await apiFetch<{ items: Project[] }>("/projects");
      setProjects(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    }
  }

  useEffect(() => {
    loadProjects();
  }, []);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await apiFetch<Project>("/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description }),
      });
      setName("");
      setDescription("");
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    }
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Projects</h1>

      <form onSubmit={onCreate} style={{ display: "grid", gap: 8, maxWidth: 480, marginBottom: 24 }}>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Project name" />
        <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" />
        <button type="submit">Create Project</button>
      </form>

      {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

      <ul>
        {projects.map((project) => (
          <li key={project.id}>
            <Link href={`/projects/${project.id}`}>{project.name}</Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
