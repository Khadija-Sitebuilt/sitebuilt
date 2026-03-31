from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
import secrets
import string
from datetime import datetime, timedelta, timezone
import httpx

from ..database import get_db
from ..dependencies.auth import get_current_user_id
from .. import models
from ..config import settings
from ..services.storage import delete_files

router = APIRouter(
    prefix="/demo",
    tags=["demo"],
)

def _format_supabase_url(url: str) -> str:
    if not url:
        return url
    if url.startswith("https://") or url.startswith("http://"):
        return url
    return f"https://{url}"


def _random_password(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _demo_domain_from_email(email: str | None) -> str:
    if not email:
        return "example.com"
    parsed = email.split("@")
    if len(parsed) != 2 or not parsed[1]:
        return "example.com"
    return parsed[1]


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        cleaned = value.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


@router.post("/session")
async def create_demo_session():
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Demo auth is not configured",
        )

    demo_domain = _demo_domain_from_email(settings.demo_user_email)
    demo_email = f"demo+{secrets.token_hex(8)}@{demo_domain}"
    demo_password = _random_password()

    supabase_url = _format_supabase_url(settings.supabase_url).rstrip("/")
    admin_url = f"{supabase_url}/auth/v1/admin/users"

    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
        "Content-Type": "application/json",
    }

    payload = {
        "email": demo_email,
        "password": demo_password,
        "email_confirm": True,
        "user_metadata": {"demo": True},
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(admin_url, headers=headers, json=payload)

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create demo user ({response.status_code})",
        )

    return {
        "email": demo_email,
        "password": demo_password,
    }


@router.post("/cleanup")
async def cleanup_demo_users(
    db: Session = Depends(get_db),
    x_demo_cleanup_token: str | None = Header(None, alias="X-Demo-Cleanup-Token"),
):
    if not settings.demo_cleanup_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Demo cleanup is not configured",
        )
    if x_demo_cleanup_token != settings.demo_cleanup_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid cleanup token",
        )
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Demo auth is not configured",
        )

    supabase_url = _format_supabase_url(settings.supabase_url).rstrip("/")
    admin_url = f"{supabase_url}/auth/v1/admin/users"
    headers = {
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "apikey": settings.supabase_service_role_key,
    }

    cutoff = datetime.now(timezone.utc) - timedelta(
        hours=settings.demo_cleanup_hours
    )
    deleted_auth_uids: list[str] = []
    deleted_supabase_users = 0

    page = 1
    per_page = 200

    async with httpx.AsyncClient(timeout=20) as client:
        while True:
            response = await client.get(
                admin_url,
                headers=headers,
                params={"page": page, "per_page": per_page},
            )
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to list demo users ({response.status_code})",
                )

            payload = response.json()
            users = payload.get("users", [])
            if not users:
                break

            for user in users:
                metadata = user.get("user_metadata") or {}
                if not metadata.get("demo"):
                    continue
                created_at = _parse_iso_datetime(user.get("created_at"))
                if not created_at or created_at > cutoff:
                    continue

                user_id = user.get("id")
                if not user_id:
                    continue

                delete_url = f"{admin_url}/{user_id}"
                delete_resp = await client.delete(
                    delete_url,
                    headers=headers,
                )
                if delete_resp.status_code < 400:
                    deleted_supabase_users += 1
                    deleted_auth_uids.append(user_id)

            if len(users) < per_page:
                break
            page += 1

    deleted_projects = 0
    deleted_plans = 0
    deleted_photos = 0
    deleted_reports = 0

    if deleted_auth_uids:
        db_users = (
            db.query(models.User)
            .filter(models.User.auth_uid.in_(deleted_auth_uids))
            .all()
        )
        for user in db_users:
            projects = (
                db.query(models.Project)
                .filter(models.Project.owner_id == user.id)
                .all()
            )

            plan_urls = []
            photo_urls = []
            report_urls = []

            for project in projects:
                plan_urls.extend(
                    [p.file_url for p in project.plans if p.file_url]
                )
                photo_urls.extend(
                    [p.file_url for p in project.photos if p.file_url]
                )
                report_urls.extend(
                    [r.file_url for r in project.reports if r.file_url]
                )

            delete_files("plans", plan_urls)
            delete_files("photos", photo_urls)
            delete_files("exports", report_urls)

            if projects:
                (
                    db.query(models.Project)
                    .filter(models.Project.owner_id == user.id)
                    .delete(synchronize_session=False)
                )
                deleted_projects += len(projects)
            db.delete(user)

            deleted_plans += len(plan_urls)
            deleted_photos += len(photo_urls)
            deleted_reports += len(report_urls)

        db.commit()

    return {
        "deleted_supabase_users": deleted_supabase_users,
        "deleted_db_users": len(deleted_auth_uids),
        "deleted_projects": deleted_projects,
        "deleted_plans": deleted_plans,
        "deleted_photos": deleted_photos,
        "deleted_reports": deleted_reports,
    }


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
