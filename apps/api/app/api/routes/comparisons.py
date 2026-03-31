from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
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
from app.services.execution_service import ExecutionService
from app.services.explanation_service import ExplanationService
from app.services.export_service import ExportService
from app.services.job_service import JobService
from app.workers.factory import get_task_queue

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

    job = JobService().create_job(
        db,
        job_type="create_comparison",
        resource_type="comparison",
        resource_id=run.id,
    )

    if settings.task_backend == "rq":
        queue_task_id = get_task_queue().enqueue("create_comparison_job", {"job_id": str(job.id)})
        return {
            "id": str(run.id),
            "job_id": str(job.id),
            "queue_task_id": queue_task_id,
            "status": run.status,
            "summary_json": run.summary_json,
        }

    try:
        ExecutionService(db).execute_comparison_job(str(job.id))
    except Exception as exc:
        safe_error = str(exc) if str(exc) else "Comparison failed"
        raise HTTPException(status_code=400, detail=safe_error) from exc

    refreshed = db.get(ComparisonRun, run.id)

    return {
        "id": str(refreshed.id),
        "job_id": str(job.id),
        "status": refreshed.status,
        "summary_json": refreshed.summary_json,
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

    before_parts_by_key: dict[str, Part] = {}
    all_before_parts = db.scalars(
        select(Part).where(Part.model_version_id == run.before_model_version_id)
    ).all()
    for part in all_before_parts:
        before_parts_by_key[part.part_key] = part

    after_parts_by_key: dict[str, Part] = {}
    all_after_parts = db.scalars(
        select(Part).where(Part.model_version_id == run.after_model_version_id)
    ).all()
    for part in all_after_parts:
        after_parts_by_key[part.part_key] = part

    after_relationship_rows = db.scalars(
        select(Relationship).where(Relationship.model_version_id == run.after_model_version_id)
    ).all()

    def _dims_from_bbox(bbox: dict) -> list[float]:
        min_corner = bbox["min"]
        max_corner = bbox["max"]
        return [
            max(float(max_corner[0] - min_corner[0]), 0.1),
            max(float(max_corner[1] - min_corner[1]), 0.1),
            max(float(max_corner[2] - min_corner[2]), 0.1),
        ]

    def _pos_from_centroid(centroid: dict) -> list[float]:
        return [float(centroid["x"]), float(centroid["y"]), float(centroid["z"])]

    def _part_for_key(part_key: str) -> Part | None:
        return after_parts_by_key.get(part_key) or before_parts_by_key.get(part_key)

    viewer_nodes: dict[str, dict] = {}
    status_rank = {"unchanged": 0, "changed": 1, "low": 2, "medium": 3, "high": 4}

    def _status_for_part(part_key: str) -> str:
        finding = next((item for item in finding_rows if item["part_key"] == part_key), None)
        if finding:
            return finding["severity"]
        changed = next(
            (
                row
                for row in diff_rows
                if row["before_part_key"] == part_key or row["after_part_key"] == part_key
            ),
            None,
        )
        if changed and changed["change_type"] != "unchanged":
            return "changed"
        return "unchanged"

    def _upsert_viewer_node(
        part_key: str,
        label: str,
        status: str,
        risk_type: str | None,
        part: Part | None,
    ) -> None:
        current = viewer_nodes.get(part_key)
        if current is not None and status_rank[status] <= status_rank.get(current["status"], 0):
            return

        viewer_nodes[part_key] = {
            "part_key": part_key,
            "label": label,
            "status": status,
            "risk_type": risk_type,
            "box": {
                "position": _pos_from_centroid(part.centroid_json) if part else [0, 0, 0],
                "dimensions": _dims_from_bbox(part.bbox_json) if part else [10, 10, 10],
            },
        }

    for part_key, part in after_parts_by_key.items():
        finding = next((item for item in finding_rows if item["part_key"] == part_key), None)
        _upsert_viewer_node(
            part_key=part_key,
            label=part.name,
            status=_status_for_part(part_key),
            risk_type=finding["risk_type"] if finding else None,
            part=part,
        )

    for row in diff_rows:
        node_status = "changed" if row["change_type"] != "unchanged" else "unchanged"
        for key in [row["before_part_key"], row["after_part_key"]]:
            if not key:
                continue
            part = _part_for_key(key)
            _upsert_viewer_node(
                part_key=key,
                label=part.name if part else key,
                status=node_status,
                risk_type=None,
                part=part,
            )

    for finding in finding_rows:
        part_key = finding["part_key"]
        if not part_key:
            continue
        part = _part_for_key(part_key)
        _upsert_viewer_node(
            part_key=part_key,
            label=finding["part_name"],
            status=finding["severity"],
            risk_type=finding["risk_type"],
            part=part,
        )

    part_by_id = {part.id: part for part in all_after_parts}
    viewer_edges: list[dict] = []
    for relationship in after_relationship_rows:
        source_part = part_by_id.get(relationship.source_part_id)
        target_part = part_by_id.get(relationship.target_part_id)
        if not source_part or not target_part:
            continue
        viewer_edges.append(
            {
                "source": source_part.part_key,
                "target": target_part.part_key,
                "relationship_type": relationship.relationship_type,
                "uncertain": False,
            }
        )

    for finding in finding_rows:
        part_key = finding["part_key"]
        if not part_key:
            continue
        changed_key = finding["evidence"].get("changed_part_key")
        if changed_key and part_key:
            viewer_edges.append(
                {
                    "source": changed_key,
                    "target": part_key,
                    "relationship_type": finding["evidence"].get("relationship_type", "related"),
                    "uncertain": bool(finding["evidence"].get("uncertain_match", False)),
                }
            )

    return {
        "comparison_id": str(run.id),
        "status": run.status,
        "diff": diff_rows,
        "summary": run.summary_json,
        "findings": finding_rows,
        "explanation": explanation,
        "viewer_payload": {
            "nodes": list(viewer_nodes.values()),
            "edges": viewer_edges,
            "legend": {
                "changed": "blue",
                "high": "red",
                "medium": "orange",
                "low": "yellow",
                "unchanged": "gray",
            },
        },
    }


@router.post("/comparisons/{comparison_id}/export")
def export_report(
    comparison_id: uuid.UUID,
    format: str = "json",
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

    exporter = ExportService()
    export_format = format.lower().strip()

    if export_format == "json":
        uri = exporter.export_report_json(str(run.id), report_payload)
        artifact_type = "json"
    elif export_format == "html":
        uri = exporter.export_report_html(str(run.id), report_payload)
        artifact_type = "html"
    elif export_format == "pdf":
        uri = exporter.export_report_pdf(str(run.id), report_payload)
        artifact_type = "pdf"
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")

    artifact = ReportArtifact(
        comparison_run_id=run.id,
        artifact_type=artifact_type,
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


@router.delete("/comparisons/{comparison_id}")
def delete_comparison(
    comparison_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    from app.services.cleanup_service import CleanupService

    run = db.get(ComparisonRun, comparison_id)
    if not run:
        raise HTTPException(status_code=404, detail="Comparison not found")

    project = db.get(Project, run.project_id)
    if not project or project.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    CleanupService().delete_comparison(db, run)
    return {"deleted": True}
