"""Fakes compartilhados pelos testes (sem rede e sem banco)."""

import os
from collections.abc import Iterator
from datetime import UTC, datetime

# `app.main` cria o `app` global ao ser importado e `Settings` exige DATABASE_URL.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")

from app.exceptions import TagGenerationError  # noqa: E402
from app.models.product import Product

DEFAULT_FAKE_TAGS = ("calcado", "corrida", "unissex", "azul", "tenis")


class FakeTagGenerator:
    """Fake de `GeminiTagGenerator`: devolve tags fixas (ou falha) e registra as chamadas."""

    def __init__(self, tags: tuple[str, ...] = DEFAULT_FAKE_TAGS, fail: bool = False) -> None:
        self.tags = tags
        self.fail = fail
        self.calls: list[tuple[str, str, tuple[str, ...]]] = []

    def generate(
        self, name: str, description: str, existing_free_tags: tuple[str, ...]
    ) -> tuple[str, ...]:
        self.calls.append((name, description, tuple(existing_free_tags)))
        if self.fail:
            raise TagGenerationError("fake generator configured to fail")
        return self.tags


class InMemoryProductRepository:
    """Fake de `ProductRepository` com a mesma interface, para testar o serviço sem Postgres.

    Usa `dict` porque é código de teste, não a estrutura principal do projeto.
    """

    def __init__(self) -> None:
        self._rows: dict[int, Product] = {}
        self._next_id = 1

    def insert(self, name: str, description: str, tags: tuple[str, ...]) -> Product:
        product = Product(
            id=self._next_id,
            name=name,
            description=description,
            tags=tags,
            created_at=datetime.now(UTC),
        )
        self._rows[product.id] = product
        self._next_id += 1
        return product

    def delete(self, product_id: int) -> bool:
        return self._rows.pop(product_id, None) is not None

    def load_all(self) -> Iterator[Product]:
        for product_id in sorted(self._rows):
            yield self._rows[product_id]
