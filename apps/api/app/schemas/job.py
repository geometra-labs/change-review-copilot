from datetime import datetime

from pydantic import BaseModel


class JobOut(BaseModel):
    id: str
    job_type: str
    resource_type: str
    resource_id: str
    status: str
    error_message: str | None
    metadata_json: dict
    created_at: datetime
    updated_at: datetime
