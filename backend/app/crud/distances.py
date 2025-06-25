from sqlalchemy.orm import Session

from ..models import Distance, Home, Location
from ..schemas.home import HomeRead
from ..schemas.location import LocationRead
from ..services.openrouteservice import OpenRouteServiceClient


def get_distance_minutes(
    home: HomeRead, location: LocationRead, ors_client: OpenRouteServiceClient
):
    return ors_client.get_route_duration_minutes(
        start_long=home.address.longitude,
        start_lat=home.address.latitude,
        end_lat=location.address.latitude,
        end_long=location.address.longitude,
    )


def create_location_distances(
    db: Session, location: LocationRead, ors_client: OpenRouteServiceClient
):
    for home in db.query(Home).all():
        try:
            distance_minutes = get_distance_minutes(home, location, ors_client)
            db_distance = Distance(
                source_home_id=home.id,
                destination_location_id=location.id,
                walking_distance_minutes=distance_minutes,
            )
            db.add(db_distance)
            db.commit()
            db.refresh(location)
        # Capture ValueErrors when no distance is found, as depending on user locations distances are sometimes not easily calculable
        except ValueError:
            print(
                f"Failed to get distance between home id: {home.id} and location {location.id}"
            )


def create_home_distances(
    db: Session, home: HomeRead, ors_client: OpenRouteServiceClient
):
    for location in db.query(Location).all():
        try:
            distance_minutes = get_distance_minutes(home, location, ors_client)
            db_distance = Distance(
                source_home_id=home.id,
                destination_location_id=location.id,
                walking_distance_minutes=distance_minutes,
            )
            db.add(db_distance)
            db.commit()
            db.refresh(home)
        # Capture ValueErrors when no distance is found, as depending on user locations distances are sometimes not easily calculable
        except ValueError:
            print(
                f"Failed to get distance between home id: {home.id} and location {location.id}"
            )


def update_home_distances(
    db: Session, home: HomeRead, ors_client: OpenRouteServiceClient
):
    # Delete existing distances where source_home_id matches the home's id
    db.query(Distance).filter(Distance.source_home_id == home.id).delete()
    db.commit()

    # Recreate distances
    create_home_distances(db, home, ors_client)


def update_location_distances(
    db: Session, location: LocationRead, ors_client: OpenRouteServiceClient
):
    # Delete existing distances where destination_location_id matches the location's id
    db.query(Distance).filter(Distance.destination_location_id == location.id).delete()
    db.commit()

    # Recreate distances
    create_location_distances(db, location, ors_client)
