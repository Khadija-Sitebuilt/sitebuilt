from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class Placement(BaseModel):
    x: float
    y: float

class PhotoWithPlacement(BaseModel):
    id: UUID
    file_url: str
    exif_lat: Optional[float]
    exif_lng: Optional[float]
    placement: Optional[Placement]

class PlanInfo(BaseModel):
    id: UUID
    file_url: str
    width: Optional[int]
    height: Optional[int]

class ReviewResponse(BaseModel):
    plan: PlanInfo
    photos: List[PhotoWithPlacement]

    class Config:
        from_attributes = True
