from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class WorkerBackend(ABC):
    @abstractmethod
    def run_parse_model_version(self, model_version_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def run_create_comparison(self, comparison_run_id: str) -> dict[str, Any]:
        raise NotImplementedError
