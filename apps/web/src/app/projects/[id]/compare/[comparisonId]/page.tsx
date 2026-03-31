"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import AppShell from "@/components/AppShell";
import SimpleAssemblyViewer from "@/components/SimpleAssemblyViewer";
import { apiFetch } from "@/lib/api";

type Report = {
  comparison_id: string;
  status: string;
  diff: Array<{
    before_part_key: string | null;
    after_part_key: string | null;
    match_confidence: number;
    match_method: string;
    change_type: string;
  }>;
  summary: {
    direct_changes: number;
    affected_parts: number;
    high_risk_count: number;
    uncertain_finding_count?: number;
    uncertain_match_count?: number;
  };
  findings: Array<{
    part_key: string | null;
    part_name: string;
    severity: string;
    risk_type: string;
    reason_text: string;
    recommended_check: string;
    rank_score: number;
    evidence: Record<string, unknown>;
  }>;
  explanation: {
    summary_text: string;
    inspect_next_text: string;
  };
  viewer_payload: {
    nodes: Array<{ part_key: string; status: string; risk_type?: string }>;
    legend: Record<string, string>;
  };
};

export default function ComparisonReportPage() {
  const params = useParams();
  const projectId = params.id as string;
  const comparisonId = params.comparisonId as string;
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!comparisonId) {
      return;
    }

    apiFetch<Report>(`/comparisons/${comparisonId}/report`)
      .then(setReport)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load report"));
  }, [comparisonId]);

  async function exportReport() {
    if (!comparisonId) {
      return;
    }

    try {
      await apiFetch<{ uri: string }>(`/comparisons/${comparisonId}/export`, {
        method: "POST",
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    }
  }

  return (
    <AppShell>
      <div style={{ padding: 24 }}>
        <p>
          <Link href={`/projects/${projectId}`}>Back to Project</Link>
        </p>

        {error ? <p style={{ color: "crimson" }}>{error}</p> : null}

        {!report ? (
          <p>Loading report...</p>
        ) : (
          <>
            <h1>Comparison Report</h1>
            <p>Status: {report.status}</p>

            <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
              <button onClick={exportReport}>Export JSON Report</button>
              <Link href={`/projects/${projectId}/compare/${comparisonId}/artifacts`}>View Artifacts</Link>
            </div>

            <section style={{ marginBottom: 24 }}>
              <h2>Summary</h2>
              <p>Direct changes: {report.summary.direct_changes}</p>
              <p>Affected parts: {report.summary.affected_parts}</p>
              <p>High-risk findings: {report.summary.high_risk_count}</p>
              <p>Uncertain findings: {report.summary.uncertain_finding_count ?? 0}</p>
              <p>Uncertain matches: {report.summary.uncertain_match_count ?? 0}</p>
            </section>

            <section style={{ marginBottom: 24 }}>
              <SimpleAssemblyViewer nodes={report.viewer_payload.nodes} />
            </section>

            <section style={{ marginBottom: 24 }}>
              <h2>Explanation</h2>
              <p>{report.explanation.summary_text}</p>
              <p>{report.explanation.inspect_next_text}</p>
            </section>

            <section style={{ marginBottom: 24 }}>
              <h2>Diff</h2>
              <table>
                <thead>
                  <tr>
                    <th>Before</th>
                    <th>After</th>
                    <th>Change Type</th>
                    <th>Method</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {report.diff.map((row, index) => (
                    <tr key={index}>
                      <td>{row.before_part_key ?? "-"}</td>
                      <td>{row.after_part_key ?? "-"}</td>
                      <td>{row.change_type}</td>
                      <td>{row.match_method}</td>
                      <td>{row.match_confidence}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>

            <section style={{ marginBottom: 24 }}>
              <h2>Findings</h2>
              {report.findings.length === 0 ? (
                <p>No affected parts exceeded the current review threshold.</p>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Part</th>
                      <th>Severity</th>
                      <th>Risk</th>
                      <th>Why Flagged</th>
                      <th>Inspect Next</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.findings.map((finding, index) => (
                      <tr key={index}>
                        <td>{finding.part_name}</td>
                        <td>{finding.severity}</td>
                        <td>{finding.risk_type}</td>
                        <td>{finding.reason_text}</td>
                        <td>{finding.recommended_check}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}
