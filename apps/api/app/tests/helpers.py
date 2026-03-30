from __future__ import annotations

import shutil
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient


def register_and_login(
    client: TestClient,
    email: str = "test@example.com",
    password: str = "password123",
) -> str:
    response = client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@contextmanager
def temporary_workspace_dir(prefix: str) -> Generator[Path, None, None]:
    root = Path("app/tests/_tmp")
    root.mkdir(parents=True, exist_ok=True)
    target = root / f"{prefix}_{uuid.uuid4().hex}"
    target.mkdir(parents=True, exist_ok=False)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)
