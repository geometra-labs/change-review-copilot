from pydantic import BaseModel
from typing import Literal, Optional


class ChangeEventCreate(BaseModel):
    change_type: Literal["dimension_changed", "part_replaced", "part_moved", "part_added_removed"]
    component_id: Optional[str] = None
    description: Optional[str] = None


class ChangeEventResponse(BaseModel):
    id: str
    change_type: str
    component_id: Optional[str] = None
    description: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class ChangeEventListResponse(BaseModel):
    change_events: list[ChangeEventResponse]
