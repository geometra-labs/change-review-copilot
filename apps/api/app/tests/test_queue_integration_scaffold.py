from __future__ import annotations

import os

import pytest


@pytest.mark.skipif(
    os.getenv("TASK_BACKEND") != "rq" or not os.getenv("TEST_REDIS_URL"),
    reason="Queue integration scaffold requires rq mode and a Redis test instance",
)
def test_queue_mode_scaffold() -> None:
    # Placeholder for a future end-to-end RQ integration test.
    # This keeps the intended test surface visible without making the default
    # test suite depend on Redis availability.
    assert True
