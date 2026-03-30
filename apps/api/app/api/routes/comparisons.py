from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.models.core import (
    ComparisonRun,
    ImpactFinding,
    ModelVersion,
    Part,
    PartMatch,
    Project,
    Relationship,
    ReportArtifact,
    User,
)
from app.db.session import get_db
from app.schemas.comparison import ComparisonCreate
from app.services.diff_service import DiffService, PartRecord
from app.services.explanation_service import ExplanationService
from app.services.export_service import ExportService
from app.services.finding_persistence_service import FindingPersistenceService
from app.services.impact_service import ImpactService
from app.services.job_service import JobService

router = APIRouter(tags=["comparisons"])


@router.post("/projects/{project_id}/comparisons")
def create_comparison(
    project_id: uuid.UUID,
    payload: ComparisonCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    before_mv = db.get(ModelVersion, payload.before_model_version_id)
    after_mv = db.get(ModelVersion, payload.after_model_version_id)
    if not before_mv or not after_mv:
        raise HTTPException(status_code=404, detail="One or more model versions not found")
    if before_mv.project_id != project_id or after_mv.project_id != project_id:
        raise HTTPException(status_code=400, detail="Model versions must belong to the same project")
    if before_mv.parse_status != "completed" or after_mv.parse_status != "completed":
        raise HTTPException(status_code=400, detail="Both model versions must be parsed before comparison")

    run = ComparisonRun(
        project_id=project_id,
        before_model_version_id=payload.before_model_version_id,
        after_model_version_id=payload.after_model_version_id,
        status="queued",
        summary_json={},
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    job_service = JobService()
    job = job_service.create_job(
        db,
        job_type="create_comparison",
        resource_type="comparison",
        resource_id=run.id,
    )
    job_service.mark_running(db, job)

    try:
        run.status = "running"
        db.commit()

        before_parts = db.scalars(select(Part).where(Part.model_version_id == before_mv.id)).all()
        after_parts = db.scalars(select(Part).where(Part.model_version_id == after_mv.id)).all()

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

        db.query(PartMatch).filter(PartMatch.comparison_run_id == run.id).delete()
        db.flush()

        for match in matches:
            part_match = PartMatch(
                comparison_run_id=run.id,
                before_part_id=before_by_key[match["before_part_key"]].id if match["before_part_key"] in before_by_key else None,
                after_part_id=after_by_key[match["after_part_key"]].id if match["after_part_key"] in after_by_key else None,
                match_confidence=match["match_confidence"],
                match_method=match["match_method"],
                change_type=match["change_type"],
            )
            db.add(part_match)

        changed_part_keys = {
            match["after_part_key"] or match["before_part_key"]
            for match in matches
            if match["change_type"] != "unchanged" and (match["after_part_key"] or match["before_part_key"])
        }

        after_relationships = db.scalars(
            select(Relationship).where(Relationship.model_version_id == after_mv.id)
        ).all()
        id_to_part = {part.id: part for part in after_parts}

        relationship_payload = []
        for rel in after_relationships:
            src = id_to_part.get(rel.source_part_id)
            dst = id_to_part.get(rel.target_part_id)
            if not src or not dst:
                continue
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
        )

        FindingPersistenceService().replace_findings(db, run, impact_payload)

        run.status = "completed"
        db.commit()
        job_service.mark_completed(
            db,
            job,
            metadata_json={"comparison_id": str(run.id), "status": run.status},
        )
    except Exception as exc:
        run.status = "failed"
        db.commit()
        job_service.mark_failed(db, job, "Comparison failed")
        raise HTTPException(status_code=500, detail="Comparison failed") from exc

    return {
        "id": str(run.id),
        "job_id": str(job.id),
        "status": run.status,
        "summary_json": run.summary_json,
    }


@router.get("/comparisons/{comparison_id}")
def get_comparison(
    comparison_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    run = db.get(ComparisonRun, comparison_id)
    if not run:
        raise HTTPException(status_code=404, detail="Comparison not found")

    project = db.get(Project, run.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {
        "id": str(run.id),
        "status": run.status,
        "summary_json": run.summary_json,
        "created_at": run.created_at.isoformat(),
    }


@router.get("/comparisons/{comparison_id}/report")
def get_report(
    comparison_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    run = db.get(ComparisonRun, comparison_id)
    if not run:
        raise HTTPException(status_code=404, detail="Comparison not found")

    project = db.get(Project, run.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    part_matches = db.scalars(
        select(PartMatch).where(PartMatch.comparison_run_id == comparison_id)
    ).all()

    findings = db.scalars(
        select(ImpactFinding)
        .where(ImpactFinding.comparison_run_id == comparison_id)
        .order_by(ImpactFinding.rank_score.desc())
    ).all()

    diff_rows = []
    for part_match in part_matches:
        before_part_key = None
        after_part_key = None
        if part_match.before_part_id:
            before_part = db.get(Part, part_match.before_part_id)
            before_part_key = before_part.part_key if before_part else None
        if part_match.after_part_id:
            after_part = db.get(Part, part_match.after_part_id)
            after_part_key = after_part.part_key if after_part else None

        diff_rows.append(
            {
                "before_part_key": before_part_key,
                "after_part_key": after_part_key,
                "match_confidence": part_match.match_confidence,
                "match_method": part_match.match_method,
                "change_type": part_match.change_type,
            }
        )

    finding_rows = []
    for finding in findings:
        part = db.get(Part, finding.part_id)
        finding_rows.append(
            {
                "part_key": part.part_key if part else None,
                "part_name": part.name if part else "Unknown Part",
                "severity": finding.severity,
                "risk_type": finding.risk_type,
                "evidence": finding.evidence_json,
                "reason_text": finding.reason_text,
                "recommended_check": finding.recommended_check,
                "rank_score": finding.rank_score,
            }
        )

    explanation = ExplanationService().build_summary(
        {"summary": run.summary_json, "findings": finding_rows}
    )

    return {
        "comparison_id": str(run.id),
        "status": run.status,
        "diff": diff_rows,
        "summary": run.summary_json,
        "findings": finding_rows,
        "explanation": explanation,
    }


@router.post("/comparisons/{comparison_id}/export")
def export_report(
    comparison_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    run = db.get(ComparisonRun, comparison_id)
    if not run:
        raise HTTPException(status_code=404, detail="Comparison not found")

    project = db.get(Project, run.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    findings = db.scalars(
        select(ImpactFinding)
        .where(ImpactFinding.comparison_run_id == comparison_id)
        .order_by(ImpactFinding.rank_score.desc())
    ).all()

    finding_rows = []
    for finding in findings:
        part = db.get(Part, finding.part_id)
        finding_rows.append(
            {
                "part_key": part.part_key if part else None,
                "part_name": part.name if part else "Unknown Part",
                "severity": finding.severity,
                "risk_type": finding.risk_type,
                "evidence": finding.evidence_json,
                "reason_text": finding.reason_text,
                "recommended_check": finding.recommended_check,
                "rank_score": finding.rank_score,
            }
        )

    report_payload = {
        "comparison_id": str(run.id),
        "summary": run.summary_json,
        "findings": finding_rows,
        "explanation": ExplanationService().build_summary(
            {"summary": run.summary_json, "findings": finding_rows}
        ),
    }

    uri = ExportService().export_report_json(str(run.id), report_payload)

    artifact = ReportArtifact(
        comparison_run_id=run.id,
        artifact_type="json",
        uri=uri,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    return {
        "artifact_id": str(artifact.id),
        "artifact_type": artifact.artifact_type,
        "uri": artifact.uri,
    }


@router.get("/comparisons/{comparison_id}/artifacts")
def list_artifacts(
    comparison_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    run = db.get(ComparisonRun, comparison_id)
    if not run:
        raise HTTPException(status_code=404, detail="Comparison not found")

    project = db.get(Project, run.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    artifacts = db.scalars(
        select(ReportArtifact)
        .where(ReportArtifact.comparison_run_id == comparison_id)
        .order_by(ReportArtifact.created_at.desc())
    ).all()

    return {
        "items": [
            {
                "id": str(artifact.id),
                "artifact_type": artifact.artifact_type,
                "uri": artifact.uri,
                "created_at": artifact.created_at.isoformat(),
            }
            for artifact in artifacts
        ]
    }
