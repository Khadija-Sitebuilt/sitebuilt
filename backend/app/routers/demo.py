from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user_id
from .. import models
from ..config import settings
from ..services.storage import delete_files

router = APIRouter(
    prefix="/demo",
    tags=["demo"],
)


@router.post("/reset")
def reset_demo_data(
    db: Session = Depends(get_db),
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_user_email: str | None = Header(None, alias="X-User-Email"),
):
    if not settings.demo_user_email:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Demo reset is not configured",
        )

    if not x_user_email or x_user_email.lower() != settings.demo_user_email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo reset is restricted",
        )

    user = get_current_user_id(x_user_id=x_user_id, db=db)

    projects = (
        db.query(models.Project)
        .filter(models.Project.owner_id == user.id)
        .all()
    )

    plan_urls = []
    photo_urls = []
    report_urls = []

    for project in projects:
        plan_urls.extend([p.file_url for p in project.plans if p.file_url])
        photo_urls.extend([p.file_url for p in project.photos if p.file_url])
        report_urls.extend([r.file_url for r in project.reports if r.file_url])

    delete_files("plans", plan_urls)
    delete_files("photos", photo_urls)
    delete_files("exports", report_urls)

    deleted_projects = len(projects)
    if deleted_projects:
        (
            db.query(models.Project)
            .filter(models.Project.owner_id == user.id)
            .delete(synchronize_session=False)
        )
        db.commit()

    return {
        "deleted_projects": deleted_projects,
        "deleted_plans": len(plan_urls),
        "deleted_photos": len(photo_urls),
        "deleted_reports": len(report_urls),
    }
