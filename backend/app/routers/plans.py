from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from pdf2image import convert_from_bytes
from PIL import Image
import uuid

from app.database import get_db
from app.dependencies.auth import get_current_user_id
from app.services.storage import upload_file, get_public_url
from .. import models

router = APIRouter(
    prefix="/projects/{project_id}/plans",
    tags=["plans"],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def upload_plan(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    pdf_bytes = file.file.read()

    images = convert_from_bytes(pdf_bytes)
    if not images:
        raise HTTPException(status_code=400, detail="Invalid PDF")

    image: Image.Image = images[0]

    width, height = image.size

    plan_id = str(uuid.uuid4())
    storage_path = f"{project_id}/{plan_id}.png"

    png_bytes = image.tobytes("raw", "RGB")
    png_image = Image.frombytes("RGB", image.size, png_bytes)

    from io import BytesIO
    buffer = BytesIO()
    png_image.save(buffer, format="PNG")
    buffer.seek(0)

    upload_file(
        bucket="plans",
        path=storage_path,
        content=buffer.read(),
        content_type="image/png",
    )

    image_url = get_public_url("plans", storage_path)

    # Check if this is the first plan (set as active default)
    existing_plans_count = db.query(models.Plan).filter(
        models.Plan.project_id == project_id
    ).count()
    is_first_plan = existing_plans_count == 0

    plan = models.Plan(
        id=plan_id,
        project_id=project_id,
        file_url=image_url,
        width=width,
        height=height,
        is_active=is_first_plan,
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return {
        "id": plan.id,
        "file_url": plan.file_url,
        "width": plan.width,
        "height": plan.height,
        "is_active": plan.is_active,
    }
