from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import crud, models, schemas
from ...services.openrouteservice import OpenRouteServiceClient
from ..dependencies import get_current_user, get_db, get_ors_client, require_role

router = APIRouter(
    prefix="/homes",
    tags=["home"],
)


@router.get("/", response_model=List[schemas.HomeRead])
def read_homes(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    users = crud.home.get_homes(db, skip=skip, limit=limit)
    return users


@router.get("/{home_id}", response_model=schemas.HomeRead)
def read_location(home_id: int, db: Session = Depends(get_db)):
    location = crud.home.get_home(db, home_id=home_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.post("/", response_model=schemas.HomeRead)
def create_home(
    home: schemas.HomeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    ors_client: OpenRouteServiceClient = Depends(get_ors_client),
):
    return crud.home.create_home(
        db=db, home=home, user_id=current_user.id, ors_client=ors_client
    )


@router.put("/{home_id}", response_model=schemas.HomeRead)
def update_home(
    home_id: int,
    home: schemas.HomeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    ors_client: OpenRouteServiceClient = Depends(get_ors_client),
):
    db_location = crud.home.get_home(db, home_id=home_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    # if db_location.creation_user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail="Not authorized to update this home"
    #     )
    return crud.home.update_home(
        db=db,
        home=home,
        home_id=home_id,
        address_id=db_location.address.id,
        ors_client=ors_client,
    )


@router.get(
    "/{home_id}/distances",
    response_model=List[schemas.DistanceRead],
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
