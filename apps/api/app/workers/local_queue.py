from __future__ import annotations

import uuid

from app.workers.queue_base import TaskQueue


class LocalImmediateQueue(TaskQueue):
    """
    Placeholder queue abstraction. It returns a synthetic queue task id while
    execution still happens inline via the local worker backend.
    """

    def enqueue(self, task_name: str, payload: dict[str, object]) -> str:
        return f"{task_name}-{uuid.uuid4()}"
