import os
import sys

import pytest
from fastapi.testclient import TestClient

# 1) Tell Python that "app" lives right here in `backend/`
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

# **1. Force an in-memory SQLite before importing your app**
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from unittest.mock import MagicMock

from app.api.dependencies import get_current_user, get_db, get_ors_client
from app.main import app
from app.models.roles import Role
from app.models.user import User
from app.utils.database import Base, SessionLocal
from app.utils.database import engine as app_engine
from app.utils.hashing import hash_password

# **2. Create a session-scoped engine** (re-using yours, if you prefer)
# If you want to isolate tests even more, you can literally re-create the engine:
# engine = create_engine(os.getenv("DATABASE_URL"), connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """Create the tables once per test session, then drop them at the end."""
    Base.metadata.create_all(bind=app_engine)
    yield
    Base.metadata.drop_all(bind=app_engine)


@pytest.fixture
def db_session():
    """
    Yield a SQLAlchemy session wrapped in a transaction,
    rolling back at the end so tests stay isolated.
    """
    connection = app_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    # begin a nested transaction (so that even commits inside your code get rolled back)
    nested = connection.begin_nested()

    yield session

    session.close()
    # rollback nested first, then the outer transaction
    nested.rollback()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_client(db_session):
    """
    Override FastAPI dependencies so that:
      - `get_db` yields our test session
      - `get_current_user` returns a fake user
      - `get_ors_client` is a MagicMock
    Then spin up TestClient(app).
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # session cleanup happens in db_session fixture

    def override_get_current_user():
        return User(
            id=1,
            name="Test User",
            email="test@example.com",
            hashed_password="fake",
            role=Role.USER,
        )

    def override_get_ors_client():
        return MagicMock()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_ors_client] = override_get_ors_client

    with TestClient(app) as tc:
        yield tc

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def add_test_user(db_session):
    # ensure there's a user with id=1 for get_current_user to point at
    test_user = User(
        id=1,
        email="testuser@example.com",
        hashed_password=hash_password("not_a_real_password"),
        role=Role.USER,
        name="testName",
    )
    db_session.add(test_user)
    db_session.commit()
    yield
