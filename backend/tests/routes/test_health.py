from fastapi.testclient import TestClient

from app.config import Settings
from app.dependencies import get_catalog_service
from app.main import create_app


def test_health_reflects_real_index_counts(client, service):
    assert client.get("/health").json() == {
        "status": "ok",
        "products": 0,
        "tags": 0,
        "gemini_configured": True,
    }

    service.create_product("Tênis Velocity", "Tênis azul para corrida")

    body = client.get("/health").json()
    assert (body["products"], body["tags"]) == (1, 5)


def test_health_reports_gemini_not_configured(service):
    app = create_app(Settings(database_url="postgresql://test"))
    app.dependency_overrides[get_catalog_service] = lambda: service

    assert TestClient(app).get("/health").json()["gemini_configured"] is False
