from datetime import UTC, datetime

import pytest

from app.exceptions import ProductNotFoundError
from app.models.product import Product
from app.services.catalog_index import CatalogIndex, SearchHit


def make_product(product_id: int, *tags: str) -> Product:
    return Product(
        id=product_id,
        name=f"Produto {product_id}",
        description="Descrição.",
        tags=tags,
        created_at=datetime(2026, 11, 21, tzinfo=UTC),
    )


def ids(hits: list[SearchHit]) -> list[int]:
    return [hit.product.id for hit in hits]


@pytest.fixture
def index() -> CatalogIndex:
    return CatalogIndex()


def test_add_then_get_and_contains(index):
    product = make_product(1, "calcado", "azul")
    index.add(product)

    assert index.get(1) is product
    assert index.contains(1)
    assert not index.contains(2)
    assert len(index) == 1


def test_get_missing_raises(index):
    with pytest.raises(ProductNotFoundError):
        index.get(99)


def test_remove_returns_product_and_unindexes_it(index):
    product = make_product(1, "azul")
    index.add(product)

    assert index.remove(1) is product
    assert not index.contains(1)
    assert index.search(("azul",)) == []


def test_remove_missing_raises(index):
    with pytest.raises(ProductNotFoundError):
        index.remove(99)


def test_remove_only_product_with_tag_drops_the_tag(index):
    index.add(make_product(1, "x", "azul"))
    index.add(make_product(2, "azul"))

    index.remove(1)

    assert dict(index.tag_counts()) == {"azul": 1}
    assert index.tag_total == 1


def test_remove_keeps_tag_while_other_products_use_it(index):
    index.add(make_product(1, "azul"))
    index.add(make_product(2, "azul"))

    index.remove(1)

    assert dict(index.tag_counts()) == {"azul": 1}
    assert ids(index.search(("azul",))) == [2]


def test_search_ranks_by_matched_terms(index):
    index.add(make_product(1, "tenis", "azul"))  # A
    index.add(make_product(2, "azul"))  # B

    hits = index.search(("tenis", "azul"))

    assert [(h.product.id, h.score) for h in hits] == [(1, 2), (2, 1)]
    assert hits[0].matched_tags == ("tenis", "azul")
    assert hits[1].matched_tags == ("azul",)


def test_search_tie_breaks_by_higher_id_first(index):
    index.add(make_product(1, "azul"))
    index.add(make_product(3, "azul"))
    index.add(make_product(2, "azul"))

    assert ids(index.search(("azul",))) == [3, 2, 1]


def test_unknown_term_does_not_score(index):
    index.add(make_product(1, "azul"))

    hits = index.search(("azul", "inexistente"))

    assert [(h.product.id, h.score) for h in hits] == [(1, 1)]


def test_only_unknown_terms_returns_empty(index):
    index.add(make_product(1, "azul"))

    assert index.search(("inexistente",)) == []


def test_search_without_terms_returns_empty(index):
    index.add(make_product(1, "azul"))

    assert index.search(()) == []


def test_list_all_most_recent_first_with_zero_score(index):
    for product_id in (2, 5, 3):
        index.add(make_product(product_id, "azul"))

    hits = index.list_all()

    assert ids(hits) == [5, 3, 2]
    assert all(hit.score == 0 and hit.matched_tags == () for hit in hits)


def test_tag_counts_sorted_by_count_then_alphabetical(index):
    index.add(make_product(1, "azul", "corrida", "calcado"))
    index.add(make_product(2, "azul", "calcado"))
    index.add(make_product(3, "azul"))

    assert index.tag_counts() == [("azul", 3), ("calcado", 2), ("corrida", 1)]
    assert index.tag_total == 3


def test_top_free_tags_ignores_base_vocabulary_and_respects_limit(index):
    index.add(make_product(1, "calcado", "azul", "leve", "tenis"))
    index.add(make_product(2, "azul", "leve", "respiravel"))
    index.add(make_product(3, "leve", "tenis"))

    assert index.top_free_tags(2) == ("leve", "tenis")
    assert index.top_free_tags(10) == ("leve", "tenis", "respiravel")


def test_empty_index(index):
    assert len(index) == 0
    assert index.tag_total == 0
    assert index.list_all() == []
    assert index.tag_counts() == []
    assert index.top_free_tags(5) == ()
