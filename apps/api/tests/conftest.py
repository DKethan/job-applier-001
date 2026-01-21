"""Pytest configuration and fixtures"""
import pytest
from pymongo import MongoClient
from pymongo.database import Database
from app.database import get_db, get_mongodb_client
from app.config import settings
import os

# Use test database
TEST_MONGODB_URI = os.getenv("TEST_MONGODB_URI", settings.mongodb_uri)
TEST_DB_NAME = os.getenv("TEST_MONGODB_TEST_DB", settings.mongodb_test_db)


@pytest.fixture
def db():
    """Create test database"""
    client = MongoClient(TEST_MONGODB_URI)
    test_db = client[TEST_DB_NAME]
    
    # Clean up before test
    test_db.users.delete_many({})
    test_db.profiles.delete_many({})
    test_db.job_postings.delete_many({})
    test_db.file_storage.delete_many({})
    
    try:
        yield test_db
    finally:
        # Clean up after test
        test_db.users.delete_many({})
        test_db.profiles.delete_many({})
        test_db.job_postings.delete_many({})
        test_db.file_storage.delete_many({})
        client.close()


@pytest.fixture
def client(db):
    """Create test client with database override"""
    from app.main import app
    from fastapi.testclient import TestClient
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
