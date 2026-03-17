"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { apiFetch } from "@/lib/api";

type Report = {
  comparison_id: string;
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
};

export default function ComparisonReportPage() {
  const params = useParams();
  const comparisonId = params.comparisonId as string;
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!comparisonId) return;

    apiFetch<Report>(`/comparisons/${comparisonId}/report`)
      .then(setReport)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load report"));
  }, [comparisonId]);

  async function exportReport() {
    if (!comparisonId) return;
    try {
      const result = await apiFetch<{ uri: string }>(`/comparisons/${comparisonId}/export`, {
        method: "POST",
      });
      alert(`Exported to ${result.uri}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    }
  }

  if (error) {
    return (
      <main style={{ padding: 24 }}>
        <p style={{ color: "crimson" }}>{error}</p>
      </main>
    );
  }

  if (!report) {
    return (
      <main style={{ padding: 24 }}>
        <p>Loading report...</p>
      </main>
    );
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>Comparison Report</h1>

      <section style={{ marginBottom: 24 }}>
        <h2>Summary</h2>
        <p>Direct changes: {report.summary.direct_changes}</p>
        <p>Affected parts: {report.summary.affected_parts}</p>
        <p>High-risk findings: {report.summary.high_risk_count}</p>
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

      <button onClick={exportReport}>Export JSON Report</button>
    </main>
  );
}
