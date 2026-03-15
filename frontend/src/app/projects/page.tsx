"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ProjectCard } from "@/components/ProjectCard";
import { api } from "@/lib/api";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<{ id: string; name: string; created_at: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.projects
      .list()
      .then((r) => setProjects(r.projects))
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading projects…</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <main>
      <h1>Projects</h1>
      <p>
        <Link href="/projects/new">New project</Link>
      </p>
      {projects.length === 0 ? (
        <p>No projects yet. Create one to get started.</p>
      ) : (
        projects.map((p) => <ProjectCard key={p.id} id={p.id} name={p.name} created_at={p.created_at} />)
      )}
    </main>
  );
}
