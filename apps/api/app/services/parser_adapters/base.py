from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.normalized_model import NormalizedAssembly


class ParserError(Exception):
    pass


class ParserAdapter(ABC):
    supported_extensions: set[str] = set()

    def can_handle(self, suffix: str) -> bool:
        return suffix.lower() in self.supported_extensions

    @abstractmethod
    def parse(self, file_uri: str) -> NormalizedAssembly:
        raise NotImplementedError
