from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..models.home import Home
from ..services.openrouteservice import OpenRouteServiceClient
from .address import create_address
from .distances import create_home_distances


def get_homes(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(models.Home).offset(skip).limit(limit).all()


def create_home(
    db: Session,
    home: schemas.HomeCreate,
    user_id: int,
    ors_client: OpenRouteServiceClient,
):
    # Create new address for new home
    db_address = create_address(db, home.address, ors_client)

    # Create new home itself
    db_home = Home(
        **home.model_dump(exclude={"address"}), creation_user_id=user_id, address_id=db_address.id
    )
    db.add(db_home)
    db.commit()
    db.refresh(db_home)

    # Create distances from home
    create_home_distances(db, db_home, ors_client)

    return db_home


# Return all distances from a home
def get_distances(db: Session, home_id: int):
    db_home = db.query(Home).filter(Home.id == home_id).first()
    return db_home.distances if db_home else None


def delete_home():
    pass
