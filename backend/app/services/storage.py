# app/services/storage.py

from supabase import create_client
from app.config import settings


supabase = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,
)


def upload_file(
    bucket: str,
    path: str,
    content: bytes,
    content_type: str,
):
    response = supabase.storage.from_(bucket).upload(
        path,
        content,
        {"content-type": content_type},
    )
    return response


def get_public_url(bucket: str, path: str) -> str:
    return supabase.storage.from_(bucket).get_public_url(path)
