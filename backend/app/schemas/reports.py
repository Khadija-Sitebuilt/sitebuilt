from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ReportRead(BaseModel):
    id: UUID
    project_id: UUID
    file_url: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True
