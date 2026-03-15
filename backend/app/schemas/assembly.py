from pydantic import BaseModel
from typing import Literal, Optional


class AssemblyCreate(BaseModel):
    name: str
    source: Literal["upload", "onshape"]
    external_id: Optional[str] = None


class AssemblyResponse(BaseModel):
    id: str
    name: str
    source: str
    project_id: str
    created_at: str

    class Config:
        from_attributes = True


class AssemblyListResponse(BaseModel):
    assemblies: list[AssemblyResponse]
