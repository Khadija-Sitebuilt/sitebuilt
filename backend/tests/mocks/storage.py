def mock_upload_file(bucket, path, content, content_type):
    return {"path": f"{bucket}/{path}"}


def mock_get_public_url(bucket, path):
    return f"https://mock.supabase/{bucket}/{path}"
