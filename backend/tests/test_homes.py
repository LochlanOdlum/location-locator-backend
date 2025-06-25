import pytest


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
    assert data["creator"]["role"] == "user"


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
