from datetime import datetime

from pydantic import BaseModel


class DistanceRead(BaseModel):
    source_home_id: int
    destination_location_id: int
    walking_distance_minutes: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
