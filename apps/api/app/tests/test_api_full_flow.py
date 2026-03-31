from __future__ import annotations

import json
from io import BytesIO

from fastapi.testclient import TestClient

from app.tests.helpers import auth_headers, register_and_login


def _fixture_bytes(payload: dict) -> BytesIO:
    return BytesIO(json.dumps(payload).encode("utf-8"))


def demo_before() -> dict:
    return {
        "assembly_id": "asm_demo_before",
        "name": "demo_enclosure_before",
        "parts": [
            {
                "part_key": "enclosure_panel",
                "name": "Enclosure Panel",
                "parent_part_key": None,
                "bbox": {"min": [0, 0, 0], "max": [100, 80, 5]},
                "centroid": {"x": 50, "y": 40, "z": 2.5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 40000,
                "geometry_signature": "sig_panel_v1",
                "metadata": {},
            },
            {
                "part_key": "mount_bracket",
                "name": "Mount Bracket",
                "parent_part_key": None,
                "bbox": {"min": [100.5, 0, 0], "max": [120.5, 20, 15]},
                "centroid": {"x": 110.5, "y": 10, "z": 7.5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 3000,
                "geometry_signature": "sig_bracket_v1",
                "metadata": {},
            },
        ],
        "relationships": [],
    }


def demo_after() -> dict:
    return {
        "assembly_id": "asm_demo_after",
        "name": "demo_enclosure_after",
        "parts": [
            {
                "part_key": "enclosure_panel",
                "name": "Enclosure Panel",
                "parent_part_key": None,
                "bbox": {"min": [0, 0, 0], "max": [92, 80, 5]},
                "centroid": {"x": 46, "y": 40, "z": 2.5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 36800,
                "geometry_signature": "sig_panel_v2",
                "metadata": {},
            },
            {
                "part_key": "mount_bracket",
                "name": "Mount Bracket",
                "parent_part_key": None,
                "bbox": {"min": [92.5, 0, 0], "max": [112.5, 20, 15]},
                "centroid": {"x": 102.5, "y": 10, "z": 7.5},
                "transform": {"translation": [0, 0, 0], "rotation": [0, 0, 0]},
                "volume_estimate": 3000,
                "geometry_signature": "sig_bracket_v1",
                "metadata": {},
            },
        ],
        "relationships": [],
    }


def test_full_api_flow(client: TestClient) -> None:
    token = register_and_login(client)
    headers = auth_headers(token)

    project_res = client.post("/projects", json={"name": "Flow Test", "description": "e2e"}, headers=headers)
    assert project_res.status_code == 200, project_res.text
    project_id = project_res.json()["id"]

    before_upload = client.post(
        f"/projects/{project_id}/model-versions",
        headers=headers,
        files={"file": ("before.json", _fixture_bytes(demo_before()), "application/json")},
        data={"label": "before", "source_type": "normalized_json"},
    )
    assert before_upload.status_code == 200, before_upload.text
    before_id = before_upload.json()["id"]

    after_upload = client.post(
        f"/projects/{project_id}/model-versions",
        headers=headers,
        files={"file": ("after.json", _fixture_bytes(demo_after()), "application/json")},
        data={"label": "after", "source_type": "normalized_json"},
    )
    assert after_upload.status_code == 200, after_upload.text
    after_id = after_upload.json()["id"]

    before_parse = client.post(f"/model-versions/{before_id}/parse", headers=headers)
    assert before_parse.status_code == 200, before_parse.text

    after_parse = client.post(f"/model-versions/{after_id}/parse", headers=headers)
    assert after_parse.status_code == 200, after_parse.text

    comparison = client.post(
        f"/projects/{project_id}/comparisons",
        json={"before_model_version_id": before_id, "after_model_version_id": after_id},
        headers=headers,
    )
    assert comparison.status_code == 200, comparison.text
    comparison_id = comparison.json()["id"]

    report = client.get(f"/comparisons/{comparison_id}/report", headers=headers)
    assert report.status_code == 200, report.text
    payload = report.json()

    assert payload["summary"]["direct_changes"] >= 1
    assert "findings" in payload
    assert "explanation" in payload
    assert "viewer_payload" in payload

    project_detail = client.get(f"/projects/{project_id}", headers=headers)
    assert project_detail.status_code == 200, project_detail.text
    detail = project_detail.json()
    assert len(detail["model_versions"]) == 2
    assert len(detail["comparisons"]) == 1
