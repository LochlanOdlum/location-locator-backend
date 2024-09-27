# tests/test_users.py

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
from app.utils.database import Base
from app.api.dependencies import get_current_user, require_role, get_db
from app.models.user import User
from app.models.roles import Role
from app import crud, schemas

# Create a test database (SQLite in-memory database)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    # Drop the tables after the test is done
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def create_test_user(db, name, email, password, role):
    user_in = schemas.UserCreate(name=name, email=email, password=password)
    user = crud.user.create_user(db=db, user=user_in)
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def test_read_users_as_admin(test_client, test_db):
    user1 = create_test_user(test_db, "User One", "user1@example.com", "password1", Role.USER)
    user2 = create_test_user(test_db, "User Two", "user2@example.com", "password2", Role.USER)
    admin_user = create_test_user(test_db, "Admin User", "admin@example.com", "adminpass", Role.ADMIN)

    def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = test_client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    user_ids = [user['id'] for user in data]
    assert user1.id in user_ids
    assert user2.id in user_ids
    assert admin_user.id in user_ids

    app.dependency_overrides.pop(get_current_user)


def test_read_users_as_user(test_client, test_db):
    user = create_test_user(test_db, "Regular User", "user@example.com", "password", Role.USER)

    def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = test_client.get("/users/")
    assert response.status_code == 403  # Forbidden

    app.dependency_overrides.pop(get_current_user)


def test_root_user_can_update_any_user(test_client, test_db):
    root_user = create_test_user(test_db, "Root User", "root@example.com", "rootpass", Role.ROOT)
    user = create_test_user(test_db, "User", "user@example.com", "password", Role.USER)

    def override_get_current_user():
        return root_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    user_update = {
        "name": "Updated User",
        "email": "updated_user@example.com",
        "role": "ADMIN",  # Change role to ADMIN
    }

    response = test_client.put(f"/users/{user.id}", json=user_update)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User"
    assert data["email"] == "updated_user@example.com"
    assert data["role"] == "ADMIN"

    app.dependency_overrides.pop(get_current_user)


def test_admin_cannot_change_user_roles(test_client, test_db):
    admin_user = create_test_user(test_db, "Admin User", "admin@example.com", "adminpass", Role.ADMIN)
    user = create_test_user(test_db, "User", "user@example.com", "password", Role.USER)

    def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    user_update = {
        "name": "User",
        "email": "user@example.com",
        "role": "ROOT",  # Attempt to change role to ROOT
    }

    response = test_client.put(f"/users/{user.id}", json=user_update)
    assert response.status_code == 403  # Forbidden
    data = response.json()
    assert data["detail"] == "Only root users can change user roles"

    app.dependency_overrides.pop(get_current_user)


def test_admin_can_update_user_profile(test_client, test_db):
    admin_user = create_test_user(test_db, "Admin User", "admin@example.com", "adminpass", Role.ADMIN)
    user = create_test_user(test_db, "User", "user@example.com", "password", Role.USER)

    def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    user_update = {
        "name": "Updated User",
        "email": "updated_user@example.com",
        "role": "USER",  # Keep the same role
    }

    response = test_client.put(f"/users/{user.id}", json=user_update)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User"
    assert data["email"] == "updated_user@example.com"
    assert data["role"] == "USER"

    app.dependency_overrides.pop(get_current_user)


def test_user_can_update_own_profile(test_client, test_db):
    user = create_test_user(test_db, "User", "user@example.com", "password", Role.USER)

    def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    user_update = {
        "name": "Updated User",
        "email": "updated_user@example.com",
        "role": "USER",  # Keep the same role
    }

    response = test_client.put(f"/users/{user.id}", json=user_update)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated User"
    assert data["email"] == "updated_user@example.com"
    assert data["role"] == "USER"

    app.dependency_overrides.pop(get_current_user)


def test_user_cannot_update_other_user_profile(test_client, test_db):
    user1 = create_test_user(test_db, "User One", "user1@example.com", "password1", Role.USER)
    user2 = create_test_user(test_db, "User Two", "user2@example.com", "password2", Role.USER)

    def override_get_current_user():
        return user1

    app.dependency_overrides[get_current_user] = override_get_current_user

    user_update = {
        "name": "User Two Updated",
        "email": "user2_updated@example.com",
        "role": "USER",
    }

    response = test_client.put(f"/users/{user2.id}", json=user_update)
    assert response.status_code == 403  # Forbidden
    data = response.json()
    assert data["detail"] == "You can only update your own profile"

    app.dependency_overrides.pop(get_current_user)


def test_user_cannot_change_own_role(test_client, test_db):
    user = create_test_user(test_db, "User", "user@example.com", "password", Role.USER)

    def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    user_update = {
        "name": "User",
        "email": "user@example.com",
        "role": "ADMIN",  # Attempt to change role
    }

    response = test_client.put(f"/users/{user.id}", json=user_update)
    assert response.status_code == 403  # Forbidden
    data = response.json()
    assert data["detail"] == "Only root users can change user roles"

    app.dependency_overrides.pop(get_current_user)


def test_root_user_cannot_make_another_user_root(test_client, test_db):
    root_user = create_test_user(test_db, "Root User", "root@example.com", "rootpass", Role.ROOT)
    user = create_test_user(test_db, "User", "user@example.com", "password", Role.USER)

    def override_get_current_user():
        return root_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    user_update = {
        "name": "User",
        "email": "user@example.com",
        "role": "ROOT",  # Attempt to make another user root
    }

    response = test_client.put(f"/users/{user.id}", json=user_update)
    assert response.status_code == 403  # Forbidden
    data = response.json()
    assert data["detail"] == "You cannot make any others root! Contact the administrator if you wish to change root user"

    app.dependency_overrides.pop(get_current_user)


def test_admin_can_delete_user(test_client, test_db):
    admin_user = create_test_user(test_db, "Admin User", "admin@example.com", "adminpass", Role.ADMIN)
    user = create_test_user(test_db, "User", "user@example.com", "password", Role.USER)

    def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = test_client.delete(f"/users/{user.id}")
    assert response.status_code == 204  # No Content

    # Verify that the user has been deleted
    deleted_user = crud.user.get_user(test_db, user_id=user.id)
    assert deleted_user is None

    app.dependency_overrides.pop(get_current_user)


def test_user_cannot_delete_user(test_client, test_db):
    user1 = create_test_user(test_db, "User One", "user1@example.com", "password1", Role.USER)
    user2 = create_test_user(test_db, "User Two", "user2@example.com", "password2", Role.USER)

    def override_get_current_user():
        return user1

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = test_client.delete(f"/users/{user2.id}")
    assert response.status_code == 403  # Forbidden

    app.dependency_overrides.pop(get_current_user)


def test_delete_nonexistent_user(test_client, test_db):
    admin_user = create_test_user(test_db, "Admin User", "admin@example.com", "adminpass", Role.ADMIN)

    # Override get_current_user to return the admin user
    def override_get_current_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = test_client.delete("/users/9999")
    assert response.status_code == 404  # Not Found
    data = response.json()
    assert data["detail"] == "User not found"

    app.dependency_overrides.pop(get_current_user)
