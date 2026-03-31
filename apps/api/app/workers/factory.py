from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import settings
from app.workers.local import LocalWorkerBackend
from app.workers.local_queue import LocalImmediateQueue
def get_worker_backend(db: Session) -> LocalWorkerBackend:
    return LocalWorkerBackend(db)


def get_task_queue():
    if settings.task_backend == "rq":
        from app.workers.rq_queue import RQTaskQueue

        return RQTaskQueue()
    return LocalImmediateQueue()
