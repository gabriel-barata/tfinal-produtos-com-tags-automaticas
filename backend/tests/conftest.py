"""Fakes compartilhados pelos testes (sem rede e sem banco)."""

from collections.abc import Iterator
from datetime import UTC, datetime

from app.models.product import Product


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
