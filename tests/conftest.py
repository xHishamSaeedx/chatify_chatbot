"""
Test configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="function")
def client():
    """Create test client"""
    with TestClient(app) as test_client:
        yield test_client
