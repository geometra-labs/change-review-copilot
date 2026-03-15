from pydantic import BaseModel
from typing import Literal, Optional


class ImpactRequest(BaseModel):
    change_event_id: str


class WarningResponse(BaseModel):
    id: str
    level: Literal["high", "medium", "low"]
    category: str
    message: str
    component_id: Optional[str] = None
    interface_id: Optional[str] = None

    class Config:
        from_attributes = True


class ImpactReportResponse(BaseModel):
    report_id: str
    change_event_id: str
    warnings: list[WarningResponse]
    affected_component_ids: list[str]
    inspect_next: list[str]
