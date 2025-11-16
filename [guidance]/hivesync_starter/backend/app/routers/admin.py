
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, schemas
from ..deps import get_admin_user

router = APIRouter()


@router.get("/me", response_model=schemas.UserRead, summary="Get current admin user (placeholder auth)")
def get_me(admin_user: models.User = Depends(get_admin_user)):
    return admin_user


@router.get("/users", response_model=list[schemas.UserRead], summary="List all users (admin only)")
def list_users(
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_admin_user),
):
    return db.query(models.User).all()
