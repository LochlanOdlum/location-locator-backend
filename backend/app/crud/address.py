from typing import Union

from sqlalchemy.orm import Session

from .. import models, schemas
from ..services.openrouteservice import OpenRouteServiceClient


def sqlalchemy_object_to_dict(obj):
    """Converts SQLAlchemy model object to a dictionary."""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def get_coordinates(
    address_data: schemas.AddressCreate, ors_client: OpenRouteServiceClient
):
    return ors_client.get_coordinates(
        f"{address_data.street}, {address_data.city}, {address_data.postal_code}, {address_data.country}"
    )


def create_address(
    db: Session,
    address_data: schemas.AddressCreate,
    ors_client: OpenRouteServiceClient,
) -> schemas.AddressRead:
    long, lat = None, None
    address_dict = address_data.model_dump()

    # If no coordinates given in input then this will attempt to find them itself
    if address_data.latitude is None or address_data.longitude is None:
        (long, lat) = get_coordinates(address_data, ors_client)
        address_dict["latitude"] = lat
        address_dict["longitude"] = long

    db_address = models.Address(**address_dict)
    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    return db_address


def update_address(
    db: Session,
    address_data: Union[schemas.AddressCreate, dict],
    existing_address_id: int,
    ors_client: OpenRouteServiceClient,
) -> schemas.AddressRead:
    # Get coordinates based on the address data
    (long, lat) = get_coordinates(address_data, ors_client)

    # Query the existing address by ID
    db_address = (
        db.query(models.Address)
        .filter(models.Address.id == existing_address_id)
        .first()
    )

    if hasattr(address_data, "model_dump"):
        address_data_dict = address_data.model_dump()
    else:
        address_data_dict = sqlalchemy_object_to_dict(address_data)

    # Update fields
    db_address.longitude = long
    db_address.latitude = lat
    for key, value in address_data_dict.items():
        setattr(db_address, key, value)

    db.commit()
    db.refresh(db_address)

    return db_address
