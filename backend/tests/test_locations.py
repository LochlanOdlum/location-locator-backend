# tests/test_locations.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.api.dependencies import get_current_user, get_ors_client, get_db
from app.utils.database import Base
from app.models.user import User
from app.models.roles import Role

# Create a test database (SQLite in-memory database)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a sessionmaker bound to the test engine
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixture to create a test location
@pytest.fixture
def test_location(test_client):
    location_data = {
        "name": "Test Location",
        "summary": "A brief summary",
        "description": "A detailed description",
        "price_estimate_min": 100,
        "price_estimate_max": 200,
        "address": {
            "street": "123 Test St",
            "city": "Testville",
            "postal_code": "12345",
            "country": "Testland",
            "latitude": 12.345678,
            "longitude": 98.765432,
        },
    }
    response = test_client.post("/locations/", json=location_data)
    assert response.status_code == 200
    return response.json()


def test_create_location(test_client):
    location_data = {
        "name": "Test Location",
        "summary": "A brief summary",
        "description": "A detailed description",
        "price_estimate_min": 100,
        "price_estimate_max": 200,
        "address": {
            "street": "123 Test St",
            "city": "Testville",
            "postal_code": "12345",
            "country": "Testland",
            "latitude": 12.345678,
            "longitude": 98.765432,
        },
    }

    response = test_client.post("/locations/", json=location_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Location"
    assert data["summary"] == "A brief summary"
    assert data["description"] == "A detailed description"
    assert data["price_estimate_min"] == 100
    assert data["price_estimate_max"] == 200
    assert data["address"]["street"] == "123 Test St"
    assert data["creator"]["email"] == "testuser@example.com"
    assert data["creator"]["role"] == "user"


def test_read_locations(test_client, test_location):
    response = test_client.get("/locations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(location["id"] == test_location["id"] for location in data)


def test_read_location_by_id(test_client, test_location):
    location_id = test_location["id"]
    response = test_client.get(f"/locations/{location_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == location_id
    assert data["name"] == "Test Location"


# def test_update_location(test_client, test_location):
#     location_id = test_location["id"]
#     updated_data = {
#         "name": "Updated Location",
#         "summary": "An updated summary",
#         "description": "An updated description",
#         "price_estimate_min": 150,
#         "price_estimate_max": 250,
#         "address": {
#             "street": "456 Updated St",
#             "city": "Newville",
#             "postal_code": "67890",
#             "country": "Newland",
#             "latitude": 23.456789,
#             "longitude": 87.654321,
#         },
#     }
#     response = test_client.put(f"/locations/{location_id}", json=updated_data)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "Updated Location"
#     assert data["summary"] == "An updated summary"
#     assert data["description"] == "An updated description"
#     assert data["price_estimate_min"] == 150
#     assert data["price_estimate_max"] == 250
#     assert data["address"]["street"] == "456 Updated St"


# def test_delete_location(test_client, test_location):
#     location_id = test_location["id"]
#     response = test_client.delete(f"/locations/{location_id}")
#     assert response.status_code == 204  # No Content

#     # Verify that the location no longer exists
#     response = test_client.get(f"/locations/{location_id}")
#     assert response.status_code == 404


def test_create_location_invalid_data(test_client):
    # Missing 'name' field
    location_data = {
        "summary": "A brief summary",
        "description": "A detailed description",
        "price_estimate_min": 100,
        "price_estimate_max": 200,
        "address": {
            "street": "123 Test St",
            "city": "Testville",
            "postal_code": "12345",
            "country": "Testland",
            "latitude": 12.345678,
            "longitude": 98.765432,
        },
    }
    response = test_client.post("/locations/", json=location_data)
    assert response.status_code == 422  # Unprocessable Entity
