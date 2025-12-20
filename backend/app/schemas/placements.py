from pydantic import BaseModel
from uuid import UUID

class PlacementCreate(BaseModel):
    plan_id: UUID
    x: float
    y: float


class PlacementRead(BaseModel):
    id: UUID
    photo_id: UUID
    plan_id: UUID
    x: float
    y: float
    placement_method: str

    class Config:
        from_attributes = True
