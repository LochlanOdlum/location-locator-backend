from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import crud, models, schemas
from ...services.openrouteservice import OpenRouteServiceClient
from ..dependencies import get_current_user, get_db, get_ors_client, require_role

router = APIRouter(
    prefix="/locations",
    tags=["locations"],
)


@router.get("/", response_model=List[schemas.LocationRead])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    locations = crud.locations.get_locations(db, skip=skip, limit=limit)
    return locations


@router.post("/", response_model=schemas.LocationRead)
def create_location(
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(get_current_user),
    ors_client: OpenRouteServiceClient = Depends(get_ors_client),
):
    return crud.locations.create_location(
        db=db, location=location, user_id=current_user.id, ors_client=ors_client
    )


@router.get("/{location_id}", response_model=schemas.LocationRead)
def read_location(location_id: int, db: Session = Depends(get_db)):
    location = crud.locations.get_location(db, location_id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.put("/{location_id}", response_model=schemas.LocationRead)
def update_location(
    location_id: int,
    location: schemas.LocationCreate,
    db: Session = Depends(get_db),
    ors_client: OpenRouteServiceClient = Depends(get_ors_client),
    current_user: schemas.UserRead = Depends(get_current_user),
):
    db_location = crud.locations.get_location(db, location_id=location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    # if db_location.creation_user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail="Not authorized to update this location"
    #     )
    return crud.locations.update_location(
        db=db,
        location=location,
        location_id=location_id,
        address_id=db_location.address.id,
        ors_client=ors_client,
    )


@router.delete(
    "/{location_id}",
    status_code=204,
    dependencies=[Depends(require_role(models.Role.ADMIN))],
)
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserRead = Depends(get_current_user),
):
    db_location = crud.locations.get_location(db, location_id=location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    # if db_location.creation_user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail="Not authorized to delete this location"
    #     )
    crud.locations.delete_location(db=db, location_id=location_id)
    return
