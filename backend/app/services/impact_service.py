import json
from sqlalchemy.orm import Session

from app.models import Assembly, ChangeEvent, ImpactReport, Warning
from app.rules.affected_parts import get_affected_part_ids
from app.rules.interfaces import get_interfaces_at_risk
from app.rules.clearance_risk import get_clearance_risks


def generate(db: Session, assembly_id: str, change_event_id: str) -> ImpactReport | None:
    assembly = db.query(Assembly).filter(Assembly.id == assembly_id).first()
    change_event = db.query(ChangeEvent).filter(
        ChangeEvent.id == change_event_id,
        ChangeEvent.assembly_id == assembly_id,
    ).first()
    if not assembly or not change_event:
        return None

    component_ids = [c.id for c in assembly.components]
    adjacency = {}  # stub: no edges for now
    affected = get_affected_part_ids(
        component_ids=component_ids,
        adjacency=adjacency,
        changed_component_id=change_event.component_id,
        change_type=change_event.change_type,
    )
    interfaces = get_interfaces_at_risk(
        adjacency=adjacency,
        changed_component_id=change_event.component_id,
    )
    clearance = get_clearance_risks(
        component_ids=component_ids,
        changed_component_id=change_event.component_id,
    )

    report = ImpactReport(
        change_event_id=change_event_id,
        assembly_id=assembly_id,
        affected_component_ids=json.dumps(affected),
        inspect_next=json.dumps(affected[:5]),
    )
    db.add(report)
    db.flush()

    for msg, level in interfaces:
        w = Warning(
            level=level,
            category="interface",
            message=msg,
            impact_report_id=report.id,
        )
        db.add(w)
    for msg, level in clearance:
        w = Warning(
            level=level,
            category="clearance",
            message=msg,
            impact_report_id=report.id,
        )
        db.add(w)

    db.commit()
    db.refresh(report)
    return report


def get_by_id(db: Session, report_id: str) -> ImpactReport | None:
    return db.query(ImpactReport).filter(ImpactReport.id == report_id).first()
