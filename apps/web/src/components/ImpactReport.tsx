"use client";

import type { ImpactReportResponse, Warning } from "@/types";

interface ImpactReportProps {
  report: ImpactReportResponse;
}

function WarningLevel({ level }: { level: string }) {
  const color = level === "high" ? "#c00" : level === "medium" ? "#960" : "#660";
  return <span style={{ color, fontWeight: 600 }}>{level}</span>;
}

export function ImpactReport({ report }: ImpactReportProps) {
  return (
    <div>
      <h2>Impact report</h2>
      <p>
        Report ID: {report.report_id} | Change event: {report.change_event_id}
      </p>

      <h3>Warnings</h3>
      {report.warnings.length === 0 ? (
        <p>No warnings.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {report.warnings.map((warning: Warning) => (
            <li
              key={warning.id}
              style={{
                borderLeft: "3px solid #ccc",
                padding: "0.5rem 0 0.5rem 0.75rem",
                marginBottom: "0.5rem",
              }}
            >
              <WarningLevel level={warning.level} /> | {warning.category}: {warning.message}
            </li>
          ))}
        </ul>
      )}

      <h3>Affected components</h3>
      {report.affected_component_ids.length === 0 ? (
        <p>None.</p>
      ) : (
        <ul>
          {report.affected_component_ids.map((id) => (
            <li key={id}>{id}</li>
          ))}
        </ul>
      )}

      <h3>Inspect next</h3>
      {report.inspect_next.length === 0 ? (
        <p>Nothing listed.</p>
      ) : (
        <ul>
          {report.inspect_next.map((id) => (
            <li key={id}>{id}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
