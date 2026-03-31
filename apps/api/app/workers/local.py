from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.core import ComparisonRun, ModelVersion, Part, PartMatch, Relationship
from app.services.diff_service import DiffService, PartRecord
from app.services.finding_persistence_service import FindingPersistenceService
from app.services.impact_service import ImpactService
from app.services.parse_service import ParseError, ParseService
from app.services.persistence_service import PersistenceService
from app.workers.base import WorkerBackend


class LocalWorkerBackend(WorkerBackend):
    """
    Runs jobs inline behind a worker interface so the execution path can be
    swapped for a real queue later without reshaping the route layer first.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def run_parse_model_version(self, model_version_id: str) -> dict[str, Any]:
        model_version = self.db.get(ModelVersion, uuid.UUID(model_version_id))
        if not model_version:
            raise ValueError("Model version not found")

        parser = ParseService()
        persistence = PersistenceService()

        model_version.parse_status = "running"
        model_version.parse_error = None
        self.db.commit()

        try:
            normalized = parser.parse_model(model_version.file_uri)
            persistence.replace_model_contents(self.db, model_version, normalized)
            self.db.commit()
            return {
                "model_version_id": str(model_version.id),
                "parse_status": model_version.parse_status,
            }
        except ParseError as exc:
            model_version.parse_status = "failed"
            model_version.parse_error = str(exc)
            self.db.commit()
            raise
        except Exception:
            model_version.parse_status = "failed"
            model_version.parse_error = "Unexpected parse failure"
            self.db.commit()
            raise

    def run_create_comparison(self, comparison_run_id: str) -> dict[str, Any]:
        run = self.db.get(ComparisonRun, uuid.UUID(comparison_run_id))
        if not run:
            raise ValueError("Comparison run not found")

        before_mv = self.db.get(ModelVersion, run.before_model_version_id)
        after_mv = self.db.get(ModelVersion, run.after_model_version_id)
        if not before_mv or not after_mv:
            raise ValueError("Linked model versions not found")

        run.status = "running"
        self.db.commit()

        before_parts = self.db.scalars(select(Part).where(Part.model_version_id == before_mv.id)).all()
        after_parts = self.db.scalars(select(Part).where(Part.model_version_id == after_mv.id)).all()

        diff_service = DiffService()
        matches = diff_service.match_parts(
            [
                PartRecord(
                    part_key=part.part_key,
                    name=part.name,
                    bbox=part.bbox_json,
                    centroid=part.centroid_json,
                    geometry_signature=part.geometry_signature,
                    parent_part_key=part.parent_part_key,
                )
                for part in before_parts
            ],
            [
                PartRecord(
                    part_key=part.part_key,
                    name=part.name,
                    bbox=part.bbox_json,
                    centroid=part.centroid_json,
                    geometry_signature=part.geometry_signature,
                    parent_part_key=part.parent_part_key,
                )
                for part in after_parts
            ],
        )

        before_by_key = {part.part_key: part for part in before_parts}
        after_by_key = {part.part_key: part for part in after_parts}

        self.db.query(PartMatch).filter(PartMatch.comparison_run_id == run.id).delete()
        self.db.flush()

        uncertain_part_keys: set[str] = set()

        for match in matches:
            self.db.add(
                PartMatch(
                    comparison_run_id=run.id,
                    before_part_id=before_by_key[match["before_part_key"]].id if match["before_part_key"] in before_by_key else None,
                    after_part_id=after_by_key[match["after_part_key"]].id if match["after_part_key"] in after_by_key else None,
                    match_confidence=match["match_confidence"],
                    match_method=match["match_method"],
                    change_type=match["change_type"],
                )
            )
            if match["change_type"] == "uncertain_match" and match["after_part_key"]:
                uncertain_part_keys.add(match["after_part_key"])

        changed_part_keys = {
            match["after_part_key"] or match["before_part_key"]
            for match in matches
            if match["change_type"] != "unchanged" and (match["after_part_key"] or match["before_part_key"])
        }

        after_relationships = self.db.scalars(
            select(Relationship).where(Relationship.model_version_id == after_mv.id)
        ).all()
        id_to_part = {part.id: part for part in after_parts}

        relationship_payload = []
        for rel in after_relationships:
            src = id_to_part.get(rel.source_part_id)
            dst = id_to_part.get(rel.target_part_id)
            if src and dst:
                relationship_payload.append(
                    {
                        "source_part_key": src.part_key,
                        "target_part_key": dst.part_key,
                        "relationship_type": rel.relationship_type,
                        "score": rel.score,
                        "evidence": rel.evidence_json,
                    }
                )

        impact_payload = ImpactService().generate_findings(
            changed_part_keys=changed_part_keys,
            parts=[{"part_key": part.part_key, "name": part.name} for part in after_parts],
            relationships=relationship_payload,
            uncertain_part_keys=uncertain_part_keys,
        )
        impact_payload["summary"]["uncertain_match_count"] = len(uncertain_part_keys)

        FindingPersistenceService().replace_findings(self.db, run, impact_payload)

        run.status = "completed"
        self.db.commit()

        return {
            "comparison_id": str(run.id),
            "status": run.status,
            "uncertain_match_count": len(uncertain_part_keys),
        }
