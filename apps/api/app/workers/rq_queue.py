from __future__ import annotations

from typing import Any

from app.config import settings
from app.workers.queue_base import TaskQueue


class RQTaskQueue(TaskQueue):
    def __init__(self) -> None:
        from redis import Redis
        from rq import Queue

        self.redis = Redis.from_url(settings.redis_url)
        self.queue = Queue("crc", connection=self.redis)

    def enqueue(self, task_name: str, payload: dict[str, Any]) -> str:
        if task_name == "parse_model_version_job":
            from app.workers.tasks import parse_model_version_job

            job = self.queue.enqueue(parse_model_version_job, payload["job_id"])
        elif task_name == "create_comparison_job":
            from app.workers.tasks import create_comparison_job

            job = self.queue.enqueue(create_comparison_job, payload["job_id"])
        else:
            raise ValueError(f"Unknown task name: {task_name}")

        return job.id
