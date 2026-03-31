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
    # Ensure HTML reports render in-browser instead of showing raw source.
    # supabase-py accepts file options; use multiple key variants for compatibility.
    response = supabase.storage.from_(bucket).upload(
        path,
        content,
        {
            "contentType": content_type,
            "content-type": content_type,
            "content_type": content_type,
            "contentDisposition": "inline",
            "content-disposition": "inline",
        },
    )
    return response


def get_public_url(bucket: str, path: str) -> str:
    return supabase.storage.from_(bucket).get_public_url(path)


def _extract_storage_path(file_url: str, bucket: str) -> str | None:
    if not file_url:
        return None
    token = f"/{bucket}/"
    if token not in file_url:
        return None
    path = file_url.split(token, 1)[1]
    if "?" in path:
        path = path.split("?", 1)[0]
    return path or None


def delete_files(bucket: str, file_urls: list[str]) -> None:
    paths = []
    for url in file_urls:
        path = _extract_storage_path(url, bucket)
        if path:
            paths.append(path)

    if not paths:
        return

    supabase.storage.from_(bucket).remove(paths)
