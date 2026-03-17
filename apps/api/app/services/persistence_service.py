from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models.core import ModelVersion, Part, Relationship
from app.schemas.normalized_model import NormalizedAssembly


class PersistenceService:
    def replace_model_contents(
        self,
        db: Session,
        model_version: ModelVersion,
        normalized: NormalizedAssembly,
    ) -> None:
        db.execute(delete(Relationship).where(Relationship.model_version_id == model_version.id))
        db.execute(delete(Part).where(Part.model_version_id == model_version.id))
        db.flush()

        persisted_parts: dict[str, Part] = {}

        for part in normalized.parts:
            row = Part(
                model_version_id=model_version.id,
                part_key=part.part_key,
                name=part.name,
                parent_part_key=part.parent_part_key,
                transform_json=part.transform.model_dump(),
                bbox_json=part.bbox.model_dump(),
                centroid_json=part.centroid.model_dump(),
                volume_estimate=part.volume_estimate,
                geometry_signature=part.geometry_signature,
                metadata_json=part.metadata,
            )
            db.add(row)
            db.flush()
            persisted_parts[part.part_key] = row

        for rel in normalized.relationships:
            row = Relationship(
                model_version_id=model_version.id,
                source_part_id=persisted_parts[rel.source_part_key].id,
                target_part_id=persisted_parts[rel.target_part_key].id,
                relationship_type=rel.relationship_type,
                score=rel.score,
                evidence_json=rel.evidence,
            )
            db.add(row)

        model_version.parse_status = "completed"
        model_version.parse_error = None
        db.flush()
