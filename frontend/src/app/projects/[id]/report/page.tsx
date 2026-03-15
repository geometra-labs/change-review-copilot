"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ImpactReport } from "@/components/ImpactReport";
import { api } from "@/lib/api";
import type { ImpactReportResponse } from "@/types";

export default function ReportPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [assemblies, setAssemblies] = useState<{ id: string; name: string; source: string }[]>([]);
  const [assemblyId, setAssemblyId] = useState("");
  const [changeEvents, setChangeEvents] = useState<{ id: string; change_type: string; created_at: string }[]>([]);
  const [changeEventId, setChangeEventId] = useState("");
  const [report, setReport] = useState<ImpactReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [genLoading, setGenLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.assemblies
      .list(projectId)
      .then((r) => {
        setAssemblies(r.assemblies);
        if (r.assemblies.length > 0) setAssemblyId(r.assemblies[0].id);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [projectId]);

  useEffect(() => {
    if (!assemblyId) return;
    api.changeEvents
      .list(projectId, assemblyId)
      .then((r) => {
        setChangeEvents(r.change_events);
        if (r.change_events.length > 0) setChangeEventId(r.change_events[0].id);
      })
      .catch(() => setChangeEvents([]));
  }, [projectId, assemblyId]);

  async function generateReport() {
    if (!assemblyId || !changeEventId) return;
    setError(null);
    setGenLoading(true);
    try {
      const r = await api.impact.generate(projectId, assemblyId, changeEventId);
      setReport({
        report_id: r.report_id,
        change_event_id: r.change_event_id,
        warnings: r.warnings,
        affected_component_ids: r.affected_component_ids,
        inspect_next: r.inspect_next,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate report");
    } finally {
      setGenLoading(false);
    }
  }

  if (loading) return <p>Loading…</p>;
  if (error && !report) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <main>
      <h1>Impact report</h1>
      <p>
        <Link href={`/projects/${projectId}`}>← Project</Link>
      </p>
      {assemblies.length === 0 ? (
        <p>Add an assembly and create a change event first.</p>
      ) : (
        <>
          <div style={{ marginTop: "1rem" }}>
            <label htmlFor="assembly">Assembly</label>
            <br />
            <select
              id="assembly"
              value={assemblyId}
              onChange={(e) => setAssemblyId(e.target.value)}
              style={{ padding: "0.5rem", marginTop: "0.25rem" }}
            >
              {assemblies.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
          <div style={{ marginTop: "0.75rem" }}>
            <label htmlFor="changeEvent">Change event</label>
            <br />
            <select
              id="changeEvent"
              value={changeEventId}
              onChange={(e) => setChangeEventId(e.target.value)}
              style={{ padding: "0.5rem", marginTop: "0.25rem" }}
            >
              {changeEvents.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.change_type} — {new Date(e.created_at).toLocaleString()}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            onClick={generateReport}
            disabled={genLoading || changeEvents.length === 0}
            style={{ marginTop: "1rem", padding: "0.5rem 1rem" }}
          >
            {genLoading ? "Generating…" : "Generate report"}
          </button>
          {error && <p style={{ color: "red", marginTop: "0.5rem" }}>{error}</p>}
          {report && (
            <div style={{ marginTop: "2rem" }}>
              <ImpactReport report={report} />
            </div>
          )}
        </>
      )}
    </main>
  );
}
