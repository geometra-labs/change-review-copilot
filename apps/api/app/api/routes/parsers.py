from __future__ import annotations

from fastapi import APIRouter

from app.services.parser_registry import ParserRegistry

router = APIRouter(prefix="/parsers", tags=["parsers"])


@router.get("/capabilities")
def list_parser_capabilities() -> dict:
    registry = ParserRegistry()
    return {
        "items": [
            {
                "name": capability.name,
                "extensions": capability.extensions,
                "supported": capability.supported,
                "notes": capability.notes,
            }
            for capability in registry.capabilities()
        ]
    }
