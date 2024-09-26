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


@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    updating_user = crud.user.get_user(db, user_id=user_id)
    if not updating_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission checks
    if current_user.role != models.Role.ROOT:
        # Non-root users cannot change roles
        if user_update.role != updating_user.role:
            raise HTTPException(
                status_code=403,
                detail="Only root users can change user roles",
            )
        
    # Non-root non-admin users can only update their own profile
    if current_user.role != models.Role.ROOT and current_user.role != models.Role.ADMIN: 
        if current_user.id != updating_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only update your own profile",
            )
        
    if user_update.role == models.Role.ROOT and (user_update.id != current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You cannot make any others root! Contact the administrator if you wish to change root user",
        )


    # Root users can update any user's profile
    updated_user = crud.user.update_user(db, updating_user=updating_user, user_update=user_update)
    return updated_user



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
