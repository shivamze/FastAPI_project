import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db

from app.core.config import settings

engine = create_engine(settings.TEST_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def setup_database():
    """Creates fresh tables before each test runs, and drops them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Changed scope to "function" to match setup_database
@pytest.fixture(scope="function")
def client(setup_database):
    """Provides the test client, dependent on the fresh database."""
    with TestClient(app) as c:
        yield c

# Changed scope to "function"
@pytest.fixture(scope="function")
def auth_token(client):
    """Creates a user in the fresh test database and logs them in."""
    client.post("/auth/register", json={
        "email": "testuser@example.com",
        "password": "testpassword123",
        "name": "Test User"
    })
    
    response = client.post("/auth/login", data={
        "username": "testuser@example.com",
        "password": "testpassword123"
    })
    
    token = response.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}