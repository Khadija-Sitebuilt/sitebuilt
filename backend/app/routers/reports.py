import uuid
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user_id
from ..schemas.reports import ReportRead
from ..services.storage import upload_file, get_public_url
from ..services.export import build_html
from .. import models

router = APIRouter(
    prefix="/projects/{project_id}/reports",
    tags=["reports"],
)


# =============================
# CREATE REPORT (Generate Export)
# =============================
@router.post("", response_model=ReportRead)
def create_report(
    project_id: str,
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

    # generate html
    plans = project.plans
    photos = project.photos

    if not plans:
        raise HTTPException(status_code=400, detail="No plans found for project")

    plan = plans[0]  # MVP: first plan only

    rows = []
    counter = 1

    for photo in photos:
        for placement in photo.placements:
            rows.append({
                "num": counter,
                "timestamp": photo.exif_timestamp,
                "x": placement.x,
                "y": placement.y,
                "method": placement.placement_method.value,
            })
            counter += 1

    html_content = build_html(project, plan, rows)

    filename = f"{project_id}/report_{uuid.uuid4()}.html"

    upload_file(
        bucket="exports",
        path=filename,
        content=html_content.encode(),
        content_type="text/html",
    )

    url = get_public_url("exports", filename)

    report = models.Report(
        project_id=project.id,
        file_url=url,
        file_type="html",
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


# =============================
# LIST REPORTS
# =============================
@router.get("", response_model=list[ReportRead])
def list_reports(
    project_id: str,
    db: Session = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    user = get_current_user_id(x_user_id=x_user_id, db=db)

    return (
        db.query(models.Report)
        .join(models.Project)
        .filter(
            models.Report.project_id == project_id,
            models.Project.owner_id == user.id,
        )
        .order_by(models.Report.created_at.desc())
        .all()
    )
