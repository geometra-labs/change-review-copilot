from __future__ import annotations

import json
from io import BytesIO

from app.tests.helpers import auth_headers, register_and_login


def _fixture_bytes(payload: dict) -> BytesIO:
    return BytesIO(json.dumps(payload).encode("utf-8"))


def payload(sig: str) -> dict:
    return {
        "assembly_id": "asm_demo",
        "name": "demo",
        "parts": [
            {
                "part_key": "panel",
                "name": "Panel",
                "parent_part_key": None,
                "bbox": {"min": [0, 0, 0], "max": [10, 10, 1]},
                "centroid": {"x": 5, "y": 5, "z": 0.5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 100,
                "geometry_signature": sig,
                "metadata": {},
            }
        ],
        "relationships": [],
    }


def test_delete_comparison_endpoint(client) -> None:
    token = register_and_login(client, "delete-cmp@test.com")
    headers = auth_headers(token)

    project = client.post("/projects", json={"name": "Delete Comparison", "description": "x"}, headers=headers)
    project_id = project.json()["id"]

    before = client.post(
        f"/projects/{project_id}/model-versions",
        headers=headers,
        files={"file": ("before.json", _fixture_bytes(payload("sig1")), "application/json")},
        data={"label": "before", "source_type": "normalized_json"},
    )
    after = client.post(
        f"/projects/{project_id}/model-versions",
        headers=headers,
        files={"file": ("after.json", _fixture_bytes(payload("sig2")), "application/json")},
        data={"label": "after", "source_type": "normalized_json"},
    )

    before_id = before.json()["id"]
    after_id = after.json()["id"]

    assert client.post(f"/model-versions/{before_id}/parse", headers=headers).status_code == 200
    assert client.post(f"/model-versions/{after_id}/parse", headers=headers).status_code == 200

    comparison = client.post(
        f"/projects/{project_id}/comparisons",
        headers=headers,
        json={"before_model_version_id": before_id, "after_model_version_id": after_id},
    )
    comparison_id = comparison.json()["id"]

    export_res = client.post(f"/comparisons/{comparison_id}/export", headers=headers)
    assert export_res.status_code == 200

    delete_res = client.delete(f"/comparisons/{comparison_id}", headers=headers)
    assert delete_res.status_code == 200
    assert delete_res.json()["deleted"] is True

    get_res = client.get(f"/comparisons/{comparison_id}", headers=headers)
    assert get_res.status_code == 404
