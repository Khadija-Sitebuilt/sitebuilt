# app/utils/uuid.py
import uuid
from fastapi import HTTPException


def parse_uuid(value: str, field_name: str = "id") -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid UUID format for {field_name}",
        )
