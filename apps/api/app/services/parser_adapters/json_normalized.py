from __future__ import annotations

import json
from pathlib import Path

from app.schemas.normalized_model import NormalizedAssembly
from app.services.parser_adapters.base import ParserAdapter, ParserError


class JsonNormalizedParserAdapter(ParserAdapter):
    supported_extensions = {".json"}

    def parse(self, file_uri: str) -> NormalizedAssembly:
        path = Path(file_uri)

        try:
            raw = json.loads(path.read_text())
        except Exception as exc:
            raise ParserError(f"Invalid JSON model: {exc}") from exc

        try:
            model = NormalizedAssembly.model_validate(raw)
        except Exception as exc:
            raise ParserError(f"Normalized model validation failed: {exc}") from exc

        self._validate_unique_part_keys(model)
        self._validate_relationship_targets(model)
        return model

    def _validate_unique_part_keys(self, model: NormalizedAssembly) -> None:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for part in model.parts:
            if part.part_key in seen:
                duplicates.add(part.part_key)
            seen.add(part.part_key)
        if duplicates:
            raise ParserError(f"Duplicate part_key values: {sorted(duplicates)}")

    def _validate_relationship_targets(self, model: NormalizedAssembly) -> None:
        keys = {part.part_key for part in model.parts}
        bad = []
        for rel in model.relationships:
            if rel.source_part_key not in keys or rel.target_part_key not in keys:
                bad.append((rel.source_part_key, rel.target_part_key))
        if bad:
            raise ParserError(f"Relationships reference missing parts: {bad}")
