from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import crud, models, schemas
from ..dependencies import get_current_user, require_role, get_db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/",
    response_model=List[schemas.UserRead],
    dependencies=[Depends(require_role(models.Role.ADMIN))],
)
def read_users(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    users = crud.user.get_users(db, skip=skip, limit=limit)
    return users


@router.delete(
    "/{user_id}",
    status_code=204,
    dependencies=[Depends(require_role(models.Role.ADMIN))],
    responses={
        204: {"description": "Success"},
        404: {"description": "User not found"},
    },
)
def deleter_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    crud.user.delete_user(db=db, user_id=user_id)
    return
