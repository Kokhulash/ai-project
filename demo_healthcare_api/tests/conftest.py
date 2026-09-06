import pytest
import httpx

BASE_URL = "http://localhost:8000"
AUTH_HEADER = {"Authorization": "Bearer test-api-token-123"}

@pytest.fixture
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c
