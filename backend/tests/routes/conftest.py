"""Fixtures das rotas: app real com `CatalogService` montado em cima dos fakes."""

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.dependencies import get_catalog_service
from app.main import create_app
from app.services.catalog_index import CatalogIndex
from app.services.catalog_service import CatalogService
from tests.conftest import FakeTagGenerator, InMemoryProductRepository

ADMIN_KEY = "test-admin-key"


@pytest.fixture
def settings() -> Settings:
    return Settings(
        database_url="postgresql://test",
        admin_key=ADMIN_KEY,
        gemini_api_key="fake-key",
        allowed_origins=["http://allowed.test"],
    )


@pytest.fixture
def generator() -> FakeTagGenerator:
    return FakeTagGenerator()


@pytest.fixture
def service(generator) -> CatalogService:
    return CatalogService(CatalogIndex(), InMemoryProductRepository(), generator)


@pytest.fixture
def client(settings, service) -> TestClient:
    """Sem `with`, o lifespan não roda: o serviço entra por `dependency_overrides`."""
    app = create_app(settings)
    app.dependency_overrides[get_catalog_service] = lambda: service
    return TestClient(app)
