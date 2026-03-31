from __future__ import annotations

from io import BytesIO

import trimesh

from app.tests.helpers import auth_headers, register_and_login


def _obj_fixture_bytes() -> BytesIO:
    mesh = trimesh.creation.box(extents=[2.0, 4.0, 6.0])
    payload = mesh.export(file_type="obj")
    if isinstance(payload, bytes):
        data = payload
    else:
        data = payload.encode("utf-8")
    return BytesIO(data)


def test_upload_and_parse_obj_mesh(client) -> None:
    token = register_and_login(client, "mesh-flow@test.com")
    headers = auth_headers(token)

    project = client.post("/projects", json={"name": "Mesh Parse", "description": "x"}, headers=headers)
    assert project.status_code == 200
    project_id = project.json()["id"]

    upload = client.post(
        f"/projects/{project_id}/model-versions",
        headers=headers,
        files={"file": ("fixture.obj", _obj_fixture_bytes(), "text/plain")},
        data={"label": "mesh", "source_type": "mesh_obj"},
    )
    assert upload.status_code == 200, upload.text
    model_version_id = upload.json()["id"]

    parse = client.post(f"/model-versions/{model_version_id}/parse", headers=headers)
    assert parse.status_code == 200, parse.text

    parts = client.get(f"/model-versions/{model_version_id}/parts", headers=headers)
    assert parts.status_code == 200, parts.text
    payload = parts.json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["part_key"].startswith("mesh_part_0_")
    assert payload["items"][0]["geometry_signature"] is not None
