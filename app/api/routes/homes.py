from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import crud, models, schemas
from ...services.openrouteservice import OpenRouteServiceClient
from ..dependencies import get_current_user, get_ors_client, require_role, get_db

router = APIRouter(
    prefix="/home",
    tags=["home"],
)


@router.get("/", response_model=List[schemas.HomeRead])
def read_homes(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    users = crud.home.get_homes(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.HomeRead)
def create_home(
    home: schemas.HomeCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(get_current_user),
    ors_client: OpenRouteServiceClient = Depends(get_ors_client),
):
    return crud.home.create_home(
        db=db, home=home, user_id=current_user.id, ors_client=ors_client
    )


@router.get(
    "/{home_id}/distances",
    response_model=List[schemas.DistanceRead],
    dependencies=[Depends(get_current_user)],
)
def get_distance(home_id: int, db: Session = Depends(get_db)):
    distances = crud.home.get_distances(db, home_id=home_id)
    if not distances:
        raise HTTPException(status_code=404, detail="Distances not found")
    return distances


@router.delete(
    "/{home_id}",
    status_code=204,
    dependencies=[Depends(require_role(models.Role.ADMIN))],
)
def delete_home(home_id: int, db: Session = Depends(get_db)):
    db_home = crud.home.get_home(db, home_id=home_id)
    if not db_home:
        raise HTTPException(status_code=404, detail="Home not found")
    crud.home.delete_home(db=db, home_id=home_id)
    return
