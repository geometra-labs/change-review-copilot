"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { AssemblyUpload } from "@/components/AssemblyUpload";

export default function AssemblyPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  return (
    <main>
      <h1>Add assembly</h1>
      <p>
        <Link href={`/projects/${projectId}`}>← Project</Link>
      </p>
      <p style={{ marginTop: "1rem" }}>Mock: enter a name and source. No file or Onshape connection yet.</p>
      <div style={{ marginTop: "1rem" }}>
        <AssemblyUpload
          projectId={projectId}
          onSuccess={() => router.push(`/projects/${projectId}`)}
        />
      </div>
    </main>
  );
}
