from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.impact_report import ImpactRequest, ImpactReportResponse, WarningResponse
from app.services import impact_service

router = APIRouter()


@router.post("/{project_id}/assemblies/{assembly_id}/impact", response_model=ImpactReportResponse)
def create_impact_report(
    project_id: str,
    assembly_id: str,
    body: ImpactRequest,
    db: Session = Depends(get_db),
):
    report = impact_service.generate(db, assembly_id, body.change_event_id)
    if not report:
        raise HTTPException(status_code=404, detail="Assembly or change event not found")
    return _report_to_response(report)


@router.get("/{project_id}/assemblies/{assembly_id}/impact/{report_id}", response_model=ImpactReportResponse)
def get_impact_report(
    project_id: str,
    assembly_id: str,
    report_id: str,
    db: Session = Depends(get_db),
):
    report = impact_service.get_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return _report_to_response(report)


def _report_to_response(report):
    import json
    return ImpactReportResponse(
        report_id=report.id,
        change_event_id=report.change_event_id,
        warnings=[
            WarningResponse(
                id=w.id,
                level=w.level,
                category=w.category,
                message=w.message,
                component_id=w.component_id,
                interface_id=w.interface_id,
            )
            for w in report.warnings
        ],
        affected_component_ids=json.loads(report.affected_component_ids or "[]"),
        inspect_next=json.loads(report.inspect_next or "[]"),
    )
