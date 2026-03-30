from __future__ import annotations

from pathlib import Path

from app.schemas.normalized_model import NormalizedAssembly
from app.services.parser_adapters.base import ParserError
from app.services.parser_adapters.json_normalized import JsonNormalizedParserAdapter
from app.services.relationship_inference_service import RelationshipInferenceService


class ParseError(Exception):
    pass


class ParseService:
    """
    Parser orchestrator. Adapters can be added incrementally without changing callers.
    """

    def __init__(self) -> None:
        self.adapters = [
            JsonNormalizedParserAdapter(),
        ]
        self.relationship_inference = RelationshipInferenceService()

    def parse_model(self, file_uri: str) -> NormalizedAssembly:
        suffix = Path(file_uri).suffix.lower()

        for adapter in self.adapters:
            if adapter.can_handle(suffix):
                try:
                    model = adapter.parse(file_uri)
                    return self.relationship_inference.infer_missing_relationships(model)
                except ParserError as exc:
                    raise ParseError(str(exc)) from exc

        raise ParseError(f"No parser implemented yet for format: {suffix}")
