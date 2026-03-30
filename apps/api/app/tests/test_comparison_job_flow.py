from __future__ import annotations

import json
from io import BytesIO

from app.tests.helpers import auth_headers, register_and_login


def _fixture_bytes(payload: dict) -> BytesIO:
    return BytesIO(json.dumps(payload).encode("utf-8"))


def payload(part_sig: str) -> dict:
    return {
        "assembly_id": "asm",
        "name": "demo",
        "parts": [
            {
                "part_key": "p1",
                "name": "Part 1",
                "parent_part_key": None,
                "bbox": {"min": [0, 0, 0], "max": [10, 10, 10]},
                "centroid": {"x": 5, "y": 5, "z": 5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 1000,
                "geometry_signature": part_sig,
                "metadata": {},
            }
        ],
        "relationships": [],
    }


def test_comparison_job_flow(client) -> None:
    token = register_and_login(client, "compare@test.com")
    headers = auth_headers(token)

    project_res = client.post("/projects", json={"name": "Cmp", "description": "x"}, headers=headers)
    project_id = project_res.json()["id"]

    before_res = client.post(
        f"/projects/{project_id}/model-versions",
        headers=headers,
        files={"file": ("before.json", _fixture_bytes(payload("sig1")), "application/json")},
        data={"label": "before", "source_type": "normalized_json"},
    )
    after_res = client.post(
        f"/projects/{project_id}/model-versions",
        headers=headers,
        files={"file": ("after.json", _fixture_bytes(payload("sig2")), "application/json")},
        data={"label": "after", "source_type": "normalized_json"},
    )

    before_id = before_res.json()["id"]
    after_id = after_res.json()["id"]

    parse_1 = client.post(f"/model-versions/{before_id}/parse", headers=headers)
    parse_2 = client.post(f"/model-versions/{after_id}/parse", headers=headers)
    assert parse_1.status_code == 200
    assert parse_2.status_code == 200

    cmp_res = client.post(
        f"/projects/{project_id}/comparisons",
        headers=headers,
        json={"before_model_version_id": before_id, "after_model_version_id": after_id},
    )
    assert cmp_res.status_code == 200, cmp_res.text
    cmp_data = cmp_res.json()
    assert cmp_data["status"] == "completed"
    assert cmp_data["job_id"]

    job_res = client.get(f"/jobs/{cmp_data['job_id']}", headers=headers)
    assert job_res.status_code == 200
    assert job_res.json()["status"] == "completed"
