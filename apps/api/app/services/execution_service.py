from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.db.models.core import ComparisonRun, JobRun, ModelVersion
from app.services.job_service import JobService
from app.workers.factory import get_worker_backend


class ExecutionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.worker = get_worker_backend(db)
        self.job_service = JobService()

    def execute_parse_job(self, job_id: str) -> dict:
        job = self.db.get(JobRun, uuid.UUID(job_id))
        if not job:
            raise ValueError("Job not found")

        model_version = self.db.get(ModelVersion, job.resource_id)
        if not model_version:
            raise ValueError("Model version not found")

        try:
            self.job_service.mark_running(self.db, job)
            result = self.worker.run_parse_model_version(str(model_version.id))
            self.job_service.mark_completed(self.db, job, metadata_json=result)
            return result
        except Exception as exc:
            safe_error = str(exc) if str(exc) else "Parse failed"
            self.job_service.mark_failed(self.db, job, safe_error)
            raise

    def execute_comparison_job(self, job_id: str) -> dict:
        job = self.db.get(JobRun, uuid.UUID(job_id))
        if not job:
            raise ValueError("Job not found")

        comparison = self.db.get(ComparisonRun, job.resource_id)
        if not comparison:
            raise ValueError("Comparison run not found")

        try:
            self.job_service.mark_running(self.db, job)
            result = self.worker.run_create_comparison(str(comparison.id))
            self.job_service.mark_completed(self.db, job, metadata_json=result)
            return result
        except Exception as exc:
            comparison.status = "failed"
            self.db.commit()
            safe_error = str(exc) if str(exc) else "Comparison failed"
            self.job_service.mark_failed(self.db, job, safe_error)
            raise
