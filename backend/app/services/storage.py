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
    # supabase-py expects "content_type" in file options (snake_case).
    # We also include other common variants for safety.
    response = supabase.storage.from_(bucket).upload(
        path,
        content,
        {
            "content_type": content_type,
            "contentType": content_type,
            "content-type": content_type,
        },
    )
    return response


def get_public_url(bucket: str, path: str) -> str:
    return supabase.storage.from_(bucket).get_public_url(path)
