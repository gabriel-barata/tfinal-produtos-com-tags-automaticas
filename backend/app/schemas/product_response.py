from datetime import datetime

from pydantic import BaseModel

from app.models.product import Product


class ProductResponse(BaseModel):
    """Produto como a API o devolve."""

    id: int
    name: str
    description: str
    tags: list[str]
    created_at: datetime

    @classmethod
    def from_entity(cls, product: Product) -> "ProductResponse":
        """Converte a entidade de domínio (tags em `tuple`) para o contrato HTTP (`list`)."""
        return cls(
            id=product.id,
            name=product.name,
            description=product.description,
            tags=list(product.tags),
            created_at=product.created_at,
        )
