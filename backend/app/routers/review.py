from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..dependencies.auth import get_current_user_id
from ..schemas.review import ReviewResponse
from .. import models

router = APIRouter(
    prefix="/projects/{project_id}/plans/{plan_id}",
    tags=["review"],
)

@router.get("/photos-with-placements", response_model=ReviewResponse)
def get_review_data(
    project_id: UUID,
    plan_id: UUID,
    db: Session = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    user = get_current_user_id(x_user_id=x_user_id, db=db)

    plan = (
        db.query(models.Plan)
        .join(models.Project)
        .filter(
            models.Plan.id == plan_id,
            models.Project.id == project_id,
            models.Project.owner_id == user.id,
        )
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    photos = (
        db.query(models.Photo)
        .filter(models.Photo.project_id == project_id)
        .all()
    )

    result = []
    for photo in photos:
        placement = next(
            (p for p in photo.placements if p.plan_id == plan.id),
            None,
        )

        result.append({
            "id": photo.id,
            "file_url": photo.file_url,
            "exif_lat": photo.exif_lat,
            "exif_lng": photo.exif_lng,
            "placement": (
                {"x": placement.x, "y": placement.y} if placement else None
            ),
        })

    return {
        "plan": {
            "id": plan.id,
            "file_url": plan.file_url,
            "width": plan.width,
            "height": plan.height,
        },
        "photos": result,
    }
