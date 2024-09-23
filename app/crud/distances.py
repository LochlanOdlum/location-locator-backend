# When customer creates location, pass this location into distances crud. It will loop through all homes and calculate the distances

# crud.create_location_distances(location):
# 	fetch list of homes. For each home, insert into distances distance from home to location
# 	will invoke get_distance(home, location)

# crud.create_home_distances(home):
# 	fetch list of locations. for each location, insert into distances distance from home to location
# 	will invoke get_distances(home, location)
from sqlalchemy.orm import Session

from ..models import Home, Location, Distance
from ..schemas.location import LocationRead
from ..schemas.home import HomeRead
from ..services.openrouteservice import OpenRouteServiceClient

def get_distance_minutes(home: HomeRead, location: LocationRead, ors_client: OpenRouteServiceClient):
  return ors_client.get_route_duration_minutes(
    start_long=home.address.longitude,
    start_lat=home.address.latitude,
    end_lat=location.address.latitude,
    end_long=location.address.longitude,
  )


def create_location_distances(db: Session, location: LocationRead, ors_client: OpenRouteServiceClient):
  for home in db.query(Home).all():
    distance_minutes = get_distance_minutes(home, location, ors_client)
    db_distance = Distance(
       source_home_id=home.id,
       destination_location_id=location.id,
       walking_distance_minutes=distance_minutes
    )
    db.add(db_distance)
    db.commit()
    db.refresh(location)


def create_home_distances(db: Session, home: HomeRead, ors_client: OpenRouteServiceClient):
  for location in db.query(Location).all():
    distance_minutes = get_distance_minutes(home, location, ors_client)
    db_distance = Distance(
       source_home_id=home.id,
       destination_location_id=location.id,
       walking_distance_minutes=distance_minutes
    )
    db.add(db_distance)
    db.commit()
    db.refresh(home)