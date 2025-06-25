from fastapi import APIRouter, Depends

from ...schemas.geocode import GeocodeSearchInput, GeocodeSearchOutput
from ...services.openrouteservice import OpenRouteServiceClient
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/geocode",
    tags=["geocode"],
)


@router.post(
    "/search/",
    response_model=GeocodeSearchOutput,
    dependencies=[Depends(get_current_user)],
)
def search_geolocation(search: GeocodeSearchInput):
    ors_client = OpenRouteServiceClient()
    (long, lat) = ors_client.get_coordinates(search.search_term)
    return GeocodeSearchOutput(longitude=long, latitude=lat)
