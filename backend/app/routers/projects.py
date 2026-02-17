# app/routers/projects.py
from typing import List
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from ..schemas.projects import ProjectCreate, ProjectRead
from ..dependencies.auth import get_current_user_id

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    user = get_current_user_id(x_user_id=x_user_id, db=db)

    project = models.Project(
        name=payload.name,
        description=payload.description,
        location=payload.location,
        start_date=payload.start_date,
        end_date=payload.end_date,
        project_manager=payload.project_manager,
        estimated_budget=payload.estimated_budget,
        owner_id=user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get(
    "",
    response_model=List[ProjectRead],
)
def list_projects(
    db: Session = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    user = get_current_user_id(x_user_id=x_user_id, db=db)

    projects = (
        db.query(models.Project)
        .filter(models.Project.owner_id == user.id)
        .order_by(models.Project.created_at.desc())
        .all()
    )
    return projects
