from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile

from app.services.storage_service import StorageService
from app.tests.helpers import temporary_workspace_dir


@pytest.mark.asyncio
async def test_storage_service_rejects_bad_extension() -> None:
    with temporary_workspace_dir("storage_bad_ext") as tmp_dir:
        service = StorageService(base_dir=str(Path(tmp_dir)))
        upload = UploadFile(filename="bad.exe", file=BytesIO(b"abc"))

        with pytest.raises(ValueError):
            await service.save_upload(upload, "project1")


@pytest.mark.asyncio
async def test_storage_service_accepts_json() -> None:
    with temporary_workspace_dir("storage_json") as tmp_dir:
        service = StorageService(base_dir=str(Path(tmp_dir)))
        upload = UploadFile(filename="demo.json", file=BytesIO(b"{}"))

        result = await service.save_upload(upload, "project1")
        assert result.size_bytes == 2
