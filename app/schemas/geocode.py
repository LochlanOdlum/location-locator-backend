from pydantic import BaseModel


class GeocodeSearchInput(BaseModel):
    search_term: str


class GeocodeSearchOutput(BaseModel):
    longitude: float
    latitude: float

