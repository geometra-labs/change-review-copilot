import uuid
from datetime import datetime

from pydantic import BaseModel


class ModelVersionOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    label: str
    source_type: str
    file_uri: str
    parse_status: str
    parse_error: str | None
    created_at: datetime


class ParseJobResponse(BaseModel):
    job_id: str
    status: str
