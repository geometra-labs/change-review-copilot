from __future__ import annotations

from fastapi.testclient import TestClient

from app.tests.helpers import auth_headers, register_and_login


def test_register_and_create_project(client: TestClient) -> None:
    token = register_and_login(client)
    headers = auth_headers(token)

    create_res = client.post(
        "/projects",
        json={"name": "Project A", "description": "desc"},
        headers=headers,
    )
    assert create_res.status_code == 200, create_res.text
    project = create_res.json()
    assert project["name"] == "Project A"

    list_res = client.get("/projects", headers=headers)
    assert list_res.status_code == 200, list_res.text
    items = list_res.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "Project A"
