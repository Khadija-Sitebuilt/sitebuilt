# app/routers/photos.py

import uuid
import shutil
import tempfile
from fastapi import APIRouter, Depends, UploadFile, File, Header, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user_id
from .. import models
from ..utils.exif import extract_exif
from ..services.storage import upload_file, get_public_url

router = APIRouter(
    prefix="/projects/{project_id}/photos",
    tags=["photos"],
)

@router.post("", status_code=201)
def upload_photo(
    project_id: str,
    file: UploadFile = File(...),
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

    # ✅ Cross-platform temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # Read bytes for upload
    with open(tmp_path, "rb") as f:
        content = f.read()

    storage_path = f"{project_id}/{uuid.uuid4()}_{file.filename}"

    upload_file(
        bucket="photos",
        path=storage_path,
        content=content,
        content_type=file.content_type or "image/jpeg",
    )

    public_url = get_public_url("photos", storage_path)

    # Extract EXIF
    lat, lng, timestamp = extract_exif(tmp_path)

    photo = models.Photo(
        project_id=project.id,
        file_url=public_url,
        exif_lat=lat,
        exif_lng=lng,
        exif_timestamp=timestamp,
    )

    db.add(photo)
    db.commit()
    db.refresh(photo)

    return photo
