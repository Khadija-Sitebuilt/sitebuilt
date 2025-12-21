from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..dependencies.auth import get_current_user_id
from ..schemas.placements import PlacementCreate, PlacementRead
from .. import models

router = APIRouter(
    prefix="/photos/{photo_id}/placements",
    tags=["placements"],
)

@router.post("", response_model=PlacementRead, status_code=status.HTTP_201_CREATED)
def create_placement(
    photo_id: UUID,
    payload: PlacementCreate,
    db: Session = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    user = get_current_user_id(x_user_id=x_user_id, db=db)

    photo = (
        db.query(models.Photo)
        .join(models.Project)
        .filter(
            models.Photo.id == photo_id,
            models.Project.owner_id == user.id,
        )
        .first()
    )
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    plan = (
        db.query(models.Plan)
        .filter_by(id=payload.plan_id, project_id=photo.project_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    placement = models.PhotoPlacement(
        photo_id=photo.id,
        plan_id=plan.id,
        x=payload.x,
        y=payload.y,
        placement_method=models.PlacementMethod.manual,
    )

    db.add(placement)
    db.commit()
    db.refresh(placement)

    return placement
