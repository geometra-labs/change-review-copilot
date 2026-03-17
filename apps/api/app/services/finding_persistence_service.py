from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models.core import ComparisonRun, ImpactFinding, Part


class FindingPersistenceService:
    def replace_findings(
        self,
        db: Session,
        comparison_run: ComparisonRun,
        findings_payload: dict,
    ) -> None:
        db.execute(delete(ImpactFinding).where(ImpactFinding.comparison_run_id == comparison_run.id))
        db.flush()

        after_parts = db.query(Part).filter(Part.model_version_id == comparison_run.after_model_version_id).all()
        after_parts_by_key = {part.part_key: part for part in after_parts}

        for finding in findings_payload["findings"]:
            part = after_parts_by_key.get(finding["part_key"])
            if not part:
                continue

            row = ImpactFinding(
                comparison_run_id=comparison_run.id,
                part_id=part.id,
                severity=finding["severity"],
                risk_type=finding["risk_type"],
                evidence_json=finding["evidence"],
                reason_text=finding["reason_text"],
                recommended_check=finding["recommended_check"],
                rank_score=finding["rank_score"],
            )
            db.add(row)

        comparison_run.summary_json = findings_payload["summary"]
        db.flush()
