from app.workers.local_queue import LocalImmediateQueue


def test_local_queue_returns_task_id() -> None:
    queue = LocalImmediateQueue()
    task_id = queue.enqueue("parse_model_version_job", {"job_id": "123"})
    assert task_id.startswith("parse_model_version_job-")
