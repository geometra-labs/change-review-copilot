import uuid

from pydantic import BaseModel


class ComparisonCreate(BaseModel):
    before_model_version_id: uuid.UUID
    after_model_version_id: uuid.UUID


class ComparisonOut(BaseModel):
    id: uuid.UUID
    status: str
    summary_json: dict


class ImpactSummaryOut(BaseModel):
    summary: dict
    findings: list[dict]
