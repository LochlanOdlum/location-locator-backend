from sqlalchemy.orm import Session

from .. import models, schemas
from ..services.openrouteservice import OpenRouteServiceClient


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
    (long, lat) = get_coordinates(address_data, ors_client)

    db_address = models.Address(
        **address_data.model_dump(), latitude=lat, longitude=long
    )
    db.add(db_address)

    db.commit()
    db.refresh(db_address)

    return db_address


def update_address(
    db: Session,
    address_data: schemas.AddressCreate,
    existing_address_id: int,
    ors_client: OpenRouteServiceClient,
) -> schemas.AddressRead:
    (long, lat) = get_coordinates(address_data, ors_client)

    db_address = (
        db.query(models.Address)
        .filter(models.Address.id == existing_address_id)
        .first()
    )

    # Update fields
    db_address.longitude = long
    db_address.latitude = lat
    for key, value in address_data.model_dump().items():
        setattr(db_address, key, value)

    db.commit()
    db.refresh(db_address)

    return db_address
