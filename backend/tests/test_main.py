import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.config import Settings
from app.exceptions import PersistenceError
from tests.conftest import InMemoryProductRepository


class FakePool:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def settings() -> Settings:
    return Settings(database_url="postgresql://test", gemini_api_key="fake-key")


def test_startup_loads_index_and_closes_pool(monkeypatch, settings):  # CA10
    repository = InMemoryProductRepository()
    repository.insert("Produto A", "Descrição do produto A", ("calcado", "corrida", "tenis"))
    pool = FakePool()
    monkeypatch.setattr(main, "create_pool", lambda url: pool)
    monkeypatch.setattr(main, "ProductRepository", lambda _pool: repository)

    with TestClient(main.create_app(settings)) as client:
        assert client.get("/health").json() == {
            "status": "ok",
            "products": 1,
            "tags": 3,
            "gemini_configured": True,
        }
        assert not pool.closed

    assert pool.closed


def test_startup_fails_fast_when_database_is_unreachable(monkeypatch, settings, caplog):
    def unreachable(url: str):
        raise PersistenceError("Não foi possível conectar ao banco de dados")

    monkeypatch.setattr(main, "create_pool", unreachable)

    with pytest.raises(PersistenceError), TestClient(main.create_app(settings)):
        pass

    assert "Startup aborted" in caplog.text


def test_startup_closes_pool_when_loading_fails(monkeypatch, settings):
    class BrokenRepository:
        def __init__(self, _pool) -> None:
            pass

        def load_all(self):
            raise PersistenceError("down")

    pool = FakePool()
    monkeypatch.setattr(main, "create_pool", lambda url: pool)
    monkeypatch.setattr(main, "ProductRepository", BrokenRepository)

    with pytest.raises(PersistenceError), TestClient(main.create_app(settings)):
        pass

    assert pool.closed
