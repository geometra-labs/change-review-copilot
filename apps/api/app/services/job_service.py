from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.db.models.core import JobRun


class JobService:
    def create_job(
        self,
        db: Session,
        *,
        job_type: str,
        resource_type: str,
        resource_id: uuid.UUID,
        metadata_json: dict | None = None,
    ) -> JobRun:
        job = JobRun(
            job_type=job_type,
            resource_type=resource_type,
            resource_id=resource_id,
            status="queued",
            metadata_json=metadata_json or {},
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def mark_running(self, db: Session, job: JobRun) -> JobRun:
        job.status = "running"
        job.error_message = None
        db.commit()
        db.refresh(job)
        return job

    def mark_completed(
        self,
        db: Session,
        job: JobRun,
        metadata_json: dict | None = None,
    ) -> JobRun:
        job.status = "completed"
        if metadata_json is not None:
            job.metadata_json = metadata_json
        job.error_message = None
        db.commit()
        db.refresh(job)
        return job

    def mark_failed(self, db: Session, job: JobRun, error_message: str) -> JobRun:
        job.status = "failed"
        job.error_message = error_message
        db.commit()
        db.refresh(job)
        return job
