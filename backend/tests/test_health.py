from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_health_check_endpoint():
    """Verify GET /api/v1/health returns 200 OK and valid health schema."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == settings.APP_VERSION
    assert data["app_name"] == settings.APP_NAME


def test_root_endpoint():
    """Verify root GET / returns 200 OK and documentation links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert data["health"] == "/api/v1/health"
