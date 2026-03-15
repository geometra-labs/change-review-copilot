from pydantic import BaseModel
from typing import Optional


class ProjectCreate(BaseModel):
    name: str


class AssemblyRef(BaseModel):
    id: str
    name: str
    source: str


class ProjectResponse(BaseModel):
    id: str
    name: str
    created_at: str
    assemblies: Optional[list[AssemblyRef]] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
