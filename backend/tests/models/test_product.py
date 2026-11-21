from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from app.models.product import Product


def make_product() -> Product:
    return Product(
        id=1,
        name="Tênis de corrida",
        description="Tênis leve para corrida de rua.",
        tags=("calcado", "corrida"),
        created_at=datetime(2026, 11, 21, tzinfo=UTC),
    )


def test_product_exposes_its_fields():
    product = make_product()

    assert product.id == 1
    assert product.name == "Tênis de corrida"
    assert product.tags == ("calcado", "corrida")


def test_product_is_immutable():
    product = make_product()

    with pytest.raises(FrozenInstanceError):
        product.name = "outro"  # type: ignore[misc]


def test_product_is_hashable_and_comparable():
    assert make_product() == make_product()
    assert hash(make_product()) == hash(make_product())
