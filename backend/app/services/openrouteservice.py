import os

import requests


class OpenRouteServiceClient:
    BASE_URL = "https://api.openrouteservice.org"

    def __init__(self, api_key: str = os.getenv("OPENROUTESERVICE_API_KEY")):
        self.api_key = api_key

    def _request(self, endpoint: str, params: dict):
        url = f"{self.BASE_URL}{endpoint}"
        headers = {"Authorization": f"{self.api_key}"}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()

    def get_coordinates(self, location_name: str):
        """Fetch GPS coordinates (longitude, latitude) for a given location string."""
        endpoint = "/geocode/search"
        params = {"text": location_name, "size": 1}
        data = self._request(endpoint, params)

        # Extract coordinates from the first result (features[0].geometry.coordinates)
        features = data.get("features")
        if not features or not features[0]:
            raise ValueError("No coordinates found for the given location.")

        coordinates = features[0]["geometry"]["coordinates"]
        longitude, latitude = coordinates[0], coordinates[1]
        return longitude, latitude

    def get_route_duration_minutes(
        self,
        start_long: float,
        start_lat: float,
        end_long: float,
        end_lat: float,
        profile="foot-walking",
    ):
        """Fetch duration in minutes between two coordinate pairs."""
        endpoint = f"/v2/directions/{profile}"

        params = {
            "start": f"{start_long},{start_lat}",
            "end": f"{end_long},{end_lat}",
        }
        data = self._request(endpoint, params)

        # Extract duration from the first result (features[0].properties.summary.duration)
        features = data.get("features")
        if (
            not features
            or not features[0]
            or "duration" not in features[0]["properties"]["summary"]
        ):
            raise ValueError("No route data found for the given coordinates.")

        duration = features[0]["properties"]["summary"]["duration"]
        return duration / 60
