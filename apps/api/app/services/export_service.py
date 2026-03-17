from __future__ import annotations

import json
from pathlib import Path


class ExportService:
    def export_report_json(self, comparison_id: str, report_payload: dict, output_dir: str = ".exports") -> str:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)

        report_path = path / f"comparison_{comparison_id}.json"
        report_path.write_text(json.dumps(report_payload, indent=2))
        return str(report_path)
