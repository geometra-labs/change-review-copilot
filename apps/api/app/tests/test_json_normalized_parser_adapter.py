import json
from pathlib import Path

from app.tests.helpers import temporary_workspace_dir
from app.services.parser_adapters.json_normalized import JsonNormalizedParserAdapter


def test_json_normalized_parser_adapter_parses_valid_model() -> None:
    payload = {
        "assembly_id": "asm",
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
            }
        ],
        "relationships": [],
    }

    with temporary_workspace_dir("json_parser") as tmp_dir:
        path = Path(tmp_dir) / "fixture.json"
        path.write_text(json.dumps(payload))

        parsed = JsonNormalizedParserAdapter().parse(str(path))
        assert parsed.assembly_id == "asm"
