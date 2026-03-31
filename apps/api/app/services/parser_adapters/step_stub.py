from __future__ import annotations

from app.schemas.normalized_model import NormalizedAssembly
from app.services.parser_adapters.base import ParserAdapter, ParserError


class StepStubParserAdapter(ParserAdapter):
    supported_extensions = {".step", ".stp"}
    is_production_ready = False
    notes = (
        "STEP parser scaffold only. Needs OpenCascade/pythonOCC or another CAD kernel. "
        "Not implemented in this repo bootstrap."
    )

    def parse(self, file_uri: str) -> NormalizedAssembly:
        raise ParserError(
            "STEP parsing is not implemented yet. Install and wire OpenCascade/pythonOCC for real STEP support."
        )
