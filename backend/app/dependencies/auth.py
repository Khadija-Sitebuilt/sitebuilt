# app/dependencies/auth.py
from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session

from .. import models


def get_current_user_id(
    x_user_id: Optional[str],
    db: Session,
):
    if db is None:
        raise RuntimeError("DB session is required")

    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header is required for now",
        )

    user = db.query(models.User).filter_by(auth_uid=x_user_id).first()
    if not user:
        user = models.User(auth_uid=x_user_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
