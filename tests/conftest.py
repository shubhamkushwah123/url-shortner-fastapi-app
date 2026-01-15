import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from main import app
from models import init_db, DBNAME

@pytest.fixture(scope="function")
def test_db():
    """Create a temporary database for testing"""
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Override the database path
    original_db = DBNAME
    import models
    models.DBNAME = temp_db.name
    
    # Initialize the test database
    init_db()
    
    yield temp_db.name
    
    # Cleanup
    os.unlink(temp_db.name)
    models.DBNAME = original_db

@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with isolated database"""
    return TestClient(app)

@pytest.fixture
def sample_urls():
    """Sample URLs for testing"""
    return [
        "https://www.google.com",
        "https://www.github.com",
        "https://stackoverflow.com/questions/123456/test",
        "https://example.com/path/to/resource?param=value&other=123"
    ]

@pytest.fixture
def sample_short_codes():
    """Sample short codes for testing"""
    return ["abc123", "xyz789", "test01", "demo02"]

@pytest.fixture(autouse=True)
def cleanup_database():
    """Auto-use fixture to cleanup database after each test"""
    yield
    # Clean up any test data after each test
    import models
    try:
        with models.sqlite3.connect(models.DBNAME) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM URLS")
            conn.commit()
    except:
        pass
