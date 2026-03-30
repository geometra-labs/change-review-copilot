"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import AppShell from "@/components/AppShell";

export default function ReportPage() {
  const params = useParams();
  const projectId = params.id as string;

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <h1>Comparison Reports Live Per Run</h1>
        <p>Reports are now attached to comparison runs instead of the older standalone report flow.</p>
        <p>
          Open a report from the comparison history on the project page, or create a new run from upload.
        </p>
        <p>
          <Link href={`/projects/${projectId}`}>Back to Project</Link>
        </p>
      </div>
    </AppShell>
  );
}
