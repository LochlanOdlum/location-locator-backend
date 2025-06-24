from sqlalchemy.orm import Session

from .. import models, schemas
from ..services.openrouteservice import OpenRouteServiceClient
from .address import create_address, update_address
from .distances import create_location_distances, update_location_distances


def get_location(db: Session, location_id: int):
    return db.query(models.Location).filter(models.Location.id == location_id).first()


def get_locations(db: Session, skip: int = 0, limit: int = 500):
    return db.query(models.Location).offset(skip).limit(limit).all()


def create_location(
    db: Session,
    location: schemas.LocationCreate,
    user_id: int,
    ors_client: OpenRouteServiceClient,
):
    # Create address for location
    db_address = create_address(db, location.address, ors_client)

    # Create location itself
    db_location = models.Location(
        **location.model_dump(exclude={"address"}), creation_user_id=user_id, address_id=db_address.id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)

    # Create distances for new location
    create_location_distances(db, db_location, ors_client)
    return db_location


def update_location(db: Session, location: schemas.LocationCreate, location_id: int, address_id: int, ors_client: OpenRouteServiceClient):
    db_location = (
        db.query(models.Location).filter(models.Location.id == location_id).first()
    )
    if db_location:
        for key, value in location.model_dump().items():
            if key not in ["address"]:
                setattr(db_location, key, value)

        # Invoke update address here
        update_address(db, location.address, address_id, ors_client)

        db.commit()
        db.refresh(db_location)

    update_location_distances(db, db_location, ors_client)

    return db_location


def delete_location(db: Session, location_id: int):
    db_location = (
        db.query(models.Location).filter(models.Location.id == location_id).first()
    )
    if db_location:
        db.delete(db_location)
        db.commit()
