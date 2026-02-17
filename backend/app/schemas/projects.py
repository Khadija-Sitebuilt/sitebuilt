# app/schemas/projects.py
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from enum import Enum


class ProjectStatus(str, Enum):
    draft = "draft"
    processing = "processing"
    for_review = "for_review"
    completed = "completed"


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    project_manager: Optional[str] = None
    estimated_budget: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: UUID
    owner_id: UUID
    status: ProjectStatus
    created_at: datetime

    class Config:
        orm_mode = True
