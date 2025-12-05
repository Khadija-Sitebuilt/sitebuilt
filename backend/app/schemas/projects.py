# app/schemas/projects.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
