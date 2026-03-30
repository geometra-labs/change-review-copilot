from __future__ import annotations

from sqlalchemy.orm import Session

from app.workers.local import LocalWorkerBackend


def get_worker_backend(db: Session) -> LocalWorkerBackend:
    return LocalWorkerBackend(db)
