"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import AppShell from "@/components/AppShell";

export default function AssemblyPage() {
  const params = useParams();
  const projectId = params.id as string;

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <h1>Assembly Flow Retired</h1>
        <p>The older assembly-only prototype flow has been replaced by the before/after upload flow.</p>
        <p>
          <Link href={`/projects/${projectId}/upload`}>Go to Upload Before / After Versions</Link>
        </p>
        <p>
          <Link href={`/projects/${projectId}`}>Back to Project</Link>
        </p>
      </div>
    </AppShell>
  );
}
