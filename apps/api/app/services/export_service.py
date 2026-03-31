from __future__ import annotations

import json
from pathlib import Path


class ExportService:
    def _ensure_dir(self, output_dir: str) -> Path:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def export_report_json(self, comparison_id: str, report_payload: dict, output_dir: str = ".exports") -> str:
        path = self._ensure_dir(output_dir)
        report_path = path / f"comparison_{comparison_id}.json"
        report_path.write_text(json.dumps(report_payload, indent=2))
        return str(report_path)

    def export_report_html(self, comparison_id: str, report_payload: dict, output_dir: str = ".exports") -> str:
        path = self._ensure_dir(output_dir)
        report_path = path / f"comparison_{comparison_id}.html"

        summary = report_payload.get("summary", {})
        findings = report_payload.get("findings", [])
        explanation = report_payload.get("explanation", {})

        findings_rows = "".join(
            f"""
            <tr>
              <td>{self._esc(finding.get("part_name", "-"))}</td>
              <td>{self._esc(finding.get("severity", "-"))}</td>
              <td>{self._esc(finding.get("risk_type", "-"))}</td>
              <td>{self._esc(finding.get("reason_text", "-"))}</td>
              <td>{self._esc(finding.get("recommended_check", "-"))}</td>
            </tr>
            """
            for finding in findings
        )

        html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Comparison Report {self._esc(comparison_id)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #111; }}
    h1, h2 {{ margin-bottom: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f7f7f7; }}
    .meta p {{ margin: 4px 0; }}
    .box {{ border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 20px; }}
  </style>
</head>
<body>
  <h1>Comparison Report</h1>

  <div class="box meta">
    <h2>Summary</h2>
    <p>Direct changes: {summary.get("direct_changes", 0)}</p>
    <p>Affected parts: {summary.get("affected_parts", 0)}</p>
    <p>High-risk findings: {summary.get("high_risk_count", 0)}</p>
    <p>Uncertain findings: {summary.get("uncertain_finding_count", 0)}</p>
    <p>Uncertain matches: {summary.get("uncertain_match_count", 0)}</p>
  </div>

  <div class="box">
    <h2>Explanation</h2>
    <p>{self._esc(explanation.get("summary_text", ""))}</p>
    <p>{self._esc(explanation.get("inspect_next_text", ""))}</p>
  </div>

  <div class="box">
    <h2>Findings</h2>
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
        {findings_rows or '<tr><td colspan="5">No findings</td></tr>'}
      </tbody>
    </table>
  </div>
</body>
</html>
        """.strip()

        report_path.write_text(html, encoding="utf-8")
        return str(report_path)

    def export_report_pdf(self, comparison_id: str, report_payload: dict, output_dir: str = ".exports") -> str:
        path = self._ensure_dir(output_dir)
        report_path = path / f"comparison_{comparison_id}.pdf"
        lines = [
            f"Comparison Report {comparison_id}",
            "",
            "Summary:",
            json.dumps(report_payload.get("summary", {}), indent=2),
            "",
            "Explanation:",
            json.dumps(report_payload.get("explanation", {}), indent=2),
            "",
            "Findings:",
            json.dumps(report_payload.get("findings", []), indent=2),
        ]

        pdf_bytes = self._build_simple_pdf(lines)
        report_path.write_bytes(pdf_bytes)
        return str(report_path)

    def _esc(self, value: object) -> str:
        string_value = str(value)
        return (
            string_value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _build_simple_pdf(self, lines: list[str]) -> bytes:
        content_lines = ["BT", "/F1 12 Tf", "72 770 Td", "14 TL"]
        for index, line in enumerate(lines):
            if index > 0:
                content_lines.append("T*")
            content_lines.append(f"({self._pdf_escape(line)}) Tj")
        content_lines.append("ET")
        content_stream = "\n".join(content_lines).encode("utf-8")

        objects = [
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
            (
                b"3 0 obj\n"
                b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\n"
                b"endobj\n"
            ),
            b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
            (
                f"5 0 obj\n<< /Length {len(content_stream)} >>\nstream\n".encode("utf-8")
                + content_stream
                + b"\nendstream\nendobj\n"
            ),
        ]

        pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for obj in objects:
            offsets.append(len(pdf))
            pdf.extend(obj)

        xref_offset = len(pdf)
        pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

        pdf.extend(
            (
                f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
                f"startxref\n{xref_offset}\n%%EOF\n"
            ).encode("ascii")
        )
        return bytes(pdf)

    def _pdf_escape(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
