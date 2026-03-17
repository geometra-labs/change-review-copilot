from pydantic import BaseModel, Field


class Vector3Object(BaseModel):
    x: float
    y: float
    z: float


class BBox(BaseModel):
    min: list[float] = Field(min_length=3, max_length=3)
    max: list[float] = Field(min_length=3, max_length=3)


class Transform(BaseModel):
    translation: list[float] = Field(min_length=3, max_length=3)
    rotation: list[float] = Field(min_length=3, max_length=3)


class NormalizedPart(BaseModel):
    part_key: str
    name: str
    parent_part_key: str | None = None
    bbox: BBox
    centroid: Vector3Object
    transform: Transform
    volume_estimate: float | None = None
    geometry_signature: str | None = None
    metadata: dict = Field(default_factory=dict)


class NormalizedRelationship(BaseModel):
    source_part_key: str
    target_part_key: str
    relationship_type: str
    score: float = 0.0
    evidence: dict = Field(default_factory=dict)


class NormalizedAssembly(BaseModel):
    assembly_id: str
    name: str
    parts: list[NormalizedPart]
    relationships: list[NormalizedRelationship]
