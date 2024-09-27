# tests/test_homes.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock

from app.main import app  # Adjust the import according to your project structure
from app.models import home, address, user, location, distance
from app.utils.database import Base
from app.api.dependencies import get_current_user, get_ors_client, get_db
from app.models.user import User
from app.models.roles import Role

# Create a test database (SQLite in-memory database)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    def override_get_current_user():
        return User(
            id=1,
            name="Test User",
            email="testuser@example.com",
            hashed_password="fakehashedpassword",
            role=Role.USER,
        )

    def override_get_ors_client():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_ors_client] = override_get_ors_client

    with TestClient(app) as client:
        yield client

    # Drop the tables after the test is done
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


# Fixture to create a test home
@pytest.fixture
def test_home(test_client):
    home_data = {
        "name": "Test Home",
        "address": {
            "street": "123 Test St",
            "city": "Testville",
            "postal_code": "12345",
            "country": "Testland",
            "latitude": 12.345678,
            "longitude": 98.765432,
        },
    }
    response = test_client.post("/homes/", json=home_data)
    assert response.status_code == 200
    return response.json()


def test_create_home(test_client):
    home_data = {
        "name": "Test Home",
        "address": {
            "street": "123 Test St",
            "city": "Testville",
            "postal_code": "12345",
            "country": "Testland",
            "latitude": 12.345678,
            "longitude": 98.765432,
        },
    }

    response = test_client.post("/homes/", json=home_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Home"
    assert data["address"]["street"] == "123 Test St"
    assert data["creator"]["email"] == "testuser@example.com"
    assert data["creator"]["role"] == "USER"


def test_read_homes(test_client, test_home):
    response = test_client.get("/homes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(home["id"] == test_home["id"] for home in data)


def test_read_home_by_id(test_client, test_home):
    home_id = test_home["id"]
    response = test_client.get(f"/homes/{home_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == home_id
    assert data["name"] == "Test Home"


def test_read_nonexistent_home(test_client):
    response = test_client.get("/homes/9999")
    assert response.status_code == 404


def test_create_home_invalid_data(test_client):
    # Missing 'name' field
    home_data = {
        "address": {
            "street": "123 Test St",
            "city": "Testville",
            "postal_code": "12345",
            "country": "Testland",
            "latitude": 12.345678,
            "longitude": 98.765432,
        },
    }
    response = test_client.post("/homes/", json=home_data)
    assert response.status_code == 422  # Unprocessable Entity
