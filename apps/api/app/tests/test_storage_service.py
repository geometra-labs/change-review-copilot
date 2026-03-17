from io import BytesIO

import pytest
from fastapi import UploadFile

from app.services.storage_service import StorageService


@pytest.mark.asyncio
async def test_storage_service_rejects_bad_extension(tmp_path) -> None:
    service = StorageService(base_dir=str(tmp_path))
    upload = UploadFile(filename="bad.exe", file=BytesIO(b"abc"))

    with pytest.raises(ValueError):
        await service.save_upload(upload, "project1")


@pytest.mark.asyncio
async def test_storage_service_accepts_json(tmp_path) -> None:
    service = StorageService(base_dir=str(tmp_path))
    upload = UploadFile(filename="demo.json", file=BytesIO(b"{}"))

    result = await service.save_upload(upload, "project1")
    assert result.size_bytes == 2
