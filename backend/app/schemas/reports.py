from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ReportRead(BaseModel):
    id: UUID
    project_id: UUID
    file_url: str
    file_type: str
    accuracy: Optional[float] = None
    created_at: datetime

    class Config:
        orm_mode = True
