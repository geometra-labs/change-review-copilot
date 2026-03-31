from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


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
        pdf = canvas.Canvas(str(report_path), pagesize=letter)
        width, height = letter
        y = height - 50

        def line(text: str, step: int = 16) -> None:
            nonlocal y
            if y < 50:
                pdf.showPage()
                y = height - 50
            pdf.drawString(40, y, text[:110])
            y -= step

        summary = report_payload.get("summary", {})
        findings = report_payload.get("findings", [])
        explanation = report_payload.get("explanation", {})

        pdf.setFont("Helvetica-Bold", 16)
        line(f"Comparison Report {comparison_id}", 24)

        pdf.setFont("Helvetica-Bold", 12)
        line("Summary", 18)
        pdf.setFont("Helvetica", 10)
        line(f"Direct changes: {summary.get('direct_changes', 0)}")
        line(f"Affected parts: {summary.get('affected_parts', 0)}")
        line(f"High-risk findings: {summary.get('high_risk_count', 0)}")
        line(f"Uncertain findings: {summary.get('uncertain_finding_count', 0)}")
        line(f"Uncertain matches: {summary.get('uncertain_match_count', 0)}", 24)

        pdf.setFont("Helvetica-Bold", 12)
        line("Explanation", 18)
        pdf.setFont("Helvetica", 10)
        for paragraph in [explanation.get("summary_text", ""), explanation.get("inspect_next_text", "")]:
            for chunk in self._wrap(paragraph, 100):
                line(chunk)
            line("", 10)

        pdf.setFont("Helvetica-Bold", 12)
        line("Findings", 18)
        pdf.setFont("Helvetica", 10)

        if not findings:
            line("No findings")
        else:
            for index, finding in enumerate(findings, start=1):
                line(f"{index}. {finding.get('part_name', '-')}", 14)
                line(f"   Severity: {finding.get('severity', '-')}")
                line(f"   Risk: {finding.get('risk_type', '-')}")
                for chunk in self._wrap(f"   Why: {finding.get('reason_text', '-')}", 100):
                    line(chunk)
                for chunk in self._wrap(f"   Inspect next: {finding.get('recommended_check', '-')}", 100):
                    line(chunk)
                line("", 10)

        pdf.save()
        return str(report_path)

    def _esc(self, value: object) -> str:
        string_value = str(value)
        return (
            string_value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _wrap(self, text: str, width: int) -> list[str]:
        words = str(text).split()
        if not words:
            return [""]

        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            if len(current) + 1 + len(word) <= width:
                current += " " + word
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines
