from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..dependencies.auth import get_current_user_id
from .. import models

router = APIRouter(
    prefix="/photos/{photo_id}",
    tags=["gps"],
)

@router.get("/gps-suggestion")
def gps_suggestion(
    photo_id: UUID,
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

    if photo.exif_lat is None or photo.exif_lng is None:
        raise HTTPException(
            status_code=400,
            detail="No GPS data available for this photo",
        )

    # ⚠️ SIMPLE STUB LOGIC (demo-only)
    BASE_X = 500
    BASE_Y = 300
    SCALE = 1000

    suggested_x = BASE_X + (photo.exif_lng % 1) * SCALE
    suggested_y = BASE_Y + (photo.exif_lat % 1) * SCALE

    return {
        "suggested_x": round(suggested_x, 2),
        "suggested_y": round(suggested_y, 2),
        "method": "gps_suggested",
    }
