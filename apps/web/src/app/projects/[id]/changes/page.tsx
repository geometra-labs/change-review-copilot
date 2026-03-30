"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import AppShell from "@/components/AppShell";

export default function ChangesPage() {
  const params = useParams();
  const projectId = params.id as string;

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <h1>Legacy Change Events Removed</h1>
        <p>This route belonged to the earlier assembly/change-event prototype and is no longer active.</p>
        <p>
          <Link href={`/projects/${projectId}/upload`}>Start a New Before / After Comparison</Link>
        </p>
        <p>
          <Link href={`/projects/${projectId}`}>Back to Project</Link>
        </p>
      </div>
    </AppShell>
  );
}
