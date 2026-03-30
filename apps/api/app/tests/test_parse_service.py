import json
from pathlib import Path

import pytest

from app.tests.helpers import temporary_workspace_dir
from app.services.parse_service import ParseError, ParseService


def test_parse_service_accepts_valid_normalized_model_and_infers_relationships() -> None:
    payload = {
        "assembly_id": "asm_1",
        "name": "demo",
        "parts": [
            {
                "part_key": "p1",
                "name": "Part 1",
                "parent_part_key": None,
                "bbox": {"min": [0, 0, 0], "max": [10, 10, 10]},
                "centroid": {"x": 5, "y": 5, "z": 5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 1.0,
                "geometry_signature": "sig1",
                "metadata": {},
            },
            {
                "part_key": "p2",
                "name": "Part 2",
                "parent_part_key": None,
                "bbox": {"min": [11, 0, 0], "max": [21, 10, 10]},
                "centroid": {"x": 16, "y": 5, "z": 5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 1.0,
                "geometry_signature": "sig2",
                "metadata": {},
            },
        ],
        "relationships": [],
    }

    with temporary_workspace_dir("parse_service_ok") as tmp_dir:
        path = Path(tmp_dir) / "demo.json"
        path.write_text(json.dumps(payload))

        parsed = ParseService().parse_model(str(path))
        assert parsed.assembly_id == "asm_1"
        assert len(parsed.relationships) >= 1


def test_parse_service_rejects_duplicate_part_keys() -> None:
    payload = {
        "assembly_id": "asm_1",
        "name": "demo",
        "parts": [
            {
                "part_key": "p1",
                "name": "Part 1",
                "parent_part_key": None,
                "bbox": {"min": [0, 0, 0], "max": [1, 1, 1]},
                "centroid": {"x": 0.5, "y": 0.5, "z": 0.5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 1.0,
                "geometry_signature": "sig1",
                "metadata": {},
            },
            {
                "part_key": "p1",
                "name": "Part 1 dup",
                "parent_part_key": None,
                "bbox": {"min": [0, 0, 0], "max": [1, 1, 1]},
                "centroid": {"x": 0.5, "y": 0.5, "z": 0.5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 1.0,
                "geometry_signature": "sig1",
                "metadata": {},
            },
        ],
        "relationships": [],
    }

    with temporary_workspace_dir("parse_service_dup") as tmp_dir:
        path = Path(tmp_dir) / "demo.json"
        path.write_text(json.dumps(payload))

        with pytest.raises(ParseError):
            ParseService().parse_model(str(path))
