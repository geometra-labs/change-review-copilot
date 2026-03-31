from __future__ import annotations

from dataclasses import dataclass

from app.services.parser_adapters.base import ParserAdapter
from app.services.parser_adapters.json_normalized import JsonNormalizedParserAdapter
from app.services.parser_adapters.mesh_stub import MeshStubParserAdapter
from app.services.parser_adapters.step_stub import StepStubParserAdapter


@dataclass(frozen=True)
class ParserCapability:
    name: str
    extensions: list[str]
    supported: bool
    notes: str


class ParserRegistry:
    def __init__(self) -> None:
        self.adapters: list[ParserAdapter] = [
            JsonNormalizedParserAdapter(),
            MeshStubParserAdapter(),
            StepStubParserAdapter(),
        ]

    def get_adapter_for_suffix(self, suffix: str) -> ParserAdapter | None:
        normalized_suffix = suffix.lower()
        for adapter in self.adapters:
            if adapter.can_handle(normalized_suffix):
                return adapter
        return None

    def capabilities(self) -> list[ParserCapability]:
        return [
            ParserCapability(
                name=adapter.__class__.__name__,
                extensions=sorted(list(adapter.supported_extensions)),
                supported=bool(getattr(adapter, "is_production_ready", False)),
                notes=str(getattr(adapter, "notes", "")),
            )
            for adapter in self.adapters
        ]
