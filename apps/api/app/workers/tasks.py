from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.services.execution_service import ExecutionService


def _session() -> Session:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    return session_local()


def parse_model_version_job(job_id: str) -> dict:
    db = _session()
    try:
        return ExecutionService(db).execute_parse_job(job_id)
    finally:
        db.close()


def create_comparison_job(job_id: str) -> dict:
    db = _session()
    try:
        return ExecutionService(db).execute_comparison_job(job_id)
    finally:
        db.close()
