from __future__ import annotations

import pathlib
import uuid
from dataclasses import dataclass

from fastapi import UploadFile

from app.config import settings


@dataclass
class StoredObject:
    uri: str
    size_bytes: int


class StorageService:
    def __init__(self, base_dir: str = ".local_storage") -> None:
        self.base_dir = pathlib.Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def validate_upload(self, file: UploadFile) -> str:
        if not file.filename:
            raise ValueError("Upload is missing a filename")

        suffix = pathlib.Path(file.filename).suffix.lower()
        if not suffix:
            raise ValueError("Upload must include a supported file extension")
        if suffix not in settings.allowed_extensions_set:
            raise ValueError(f"Unsupported file extension: {suffix}")
        return suffix

    async def save_upload(self, file: UploadFile, project_id: str) -> StoredObject:
        suffix = self.validate_upload(file)
        file_id = uuid.uuid4().hex
        target_dir = self.base_dir / project_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{file_id}{suffix}"

        content = await file.read()
        if not content:
            raise ValueError("Upload is empty")

        max_bytes = settings.max_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise ValueError("Upload exceeds configured size limit")

        target_path.write_bytes(content)
        return StoredObject(uri=str(target_path), size_bytes=len(content))
