
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .db import get_db
from . import models


def get_admin_user(db: Session = Depends(get_db)) -> models.User:
    # NOTE: This is a placeholder. In a full implementation, you'd parse a JWT from Authorization header.
    # For now, we just grab the first admin user.
    admin = db.query(models.User).filter(models.User.is_admin == True).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No admin user exists. Run admin_bootstrap.py to create one.",
        )
    return admin
