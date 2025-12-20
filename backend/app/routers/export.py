from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..dependencies.auth import get_current_user_id
from .. import models
from ..services.export import generate_export

router = APIRouter(
    prefix="/projects/{project_id}",
    tags=["export"],
)

@router.post("/export")
def export_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    user = get_current_user_id(x_user_id=x_user_id, db=db)

    project = (
        db.query(models.Project)
        .filter_by(id=project_id, owner_id=user.id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    export_url = generate_export(project, db)

    return {
        "project_id": project_id,
        "export_url": export_url,
    }
