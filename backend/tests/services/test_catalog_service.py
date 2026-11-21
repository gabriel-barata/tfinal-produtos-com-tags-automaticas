import pytest

from app.exceptions import PersistenceError, ProductNotFoundError, TagGenerationError
from app.models.product import Product
from app.models.tag_vocabulary import TagGroup
from app.services.catalog_index import CatalogIndex
from app.services.catalog_service import CatalogService
from tests.conftest import FakeTagGenerator, InMemoryProductRepository


class FailingRepository(InMemoryProductRepository):
    """Repositório que falha nas operações escolhidas, para testar a consistência."""

    def __init__(self, fail_insert: bool = False, fail_delete: bool = False) -> None:
        super().__init__()
        self.fail_insert = fail_insert
        self.fail_delete = fail_delete
        self.delete_calls = 0

    def insert(self, name: str, description: str, tags: tuple[str, ...]) -> Product:
        if self.fail_insert:
            raise PersistenceError("insert failed")
        return super().insert(name, description, tags)

    def delete(self, product_id: int) -> bool:
        self.delete_calls += 1
        if self.fail_delete:
            raise PersistenceError("delete failed")
        return super().delete(product_id)


@pytest.fixture
def index() -> CatalogIndex:
    return CatalogIndex()


@pytest.fixture
def repository() -> InMemoryProductRepository:
    return InMemoryProductRepository()


@pytest.fixture
def generator() -> FakeTagGenerator:
    return FakeTagGenerator()


@pytest.fixture
def service(index, repository, generator) -> CatalogService:
    return CatalogService(index, repository, generator)


def test_create_product_saves_and_indexes(service, index, repository, generator):
    product = service.create_product("Tênis Velocity", "Tênis azul para corrida")

    assert product.tags == generator.tags
    assert service.get_product(product.id) is product
    assert list(repository.load_all()) == [product]
    assert index.contains(product.id)


def test_create_product_passes_existing_free_tags_to_generator(service, generator):
    service.create_product("Tênis Velocity", "Tênis azul para corrida")
    service.create_product("Tênis Trail", "Tênis para trilha")

    assert generator.calls[0][2] == ()
    assert "tenis" in generator.calls[1][2]


def test_create_product_generator_failure_touches_nothing(index, repository, generator):  # CA7
    generator.fail = True
    service = CatalogService(index, repository, generator)

    with pytest.raises(TagGenerationError):
        service.create_product("Tênis Velocity", "Tênis azul para corrida")

    assert list(repository.load_all()) == []
    assert len(index) == 0


def test_create_product_insert_failure_indexes_nothing(index, generator):
    service = CatalogService(index, FailingRepository(fail_insert=True), generator)

    with pytest.raises(PersistenceError):
        service.create_product("Tênis Velocity", "Tênis azul para corrida")

    assert len(index) == 0


def test_create_product_logs_and_propagates_index_failure(
    repository, generator, caplog, monkeypatch
):
    index = CatalogIndex()
    monkeypatch.setattr(index, "add", lambda product: 1 / 0)
    service = CatalogService(index, repository, generator)

    with pytest.raises(ZeroDivisionError):
        service.create_product("Tênis Velocity", "Tênis azul para corrida")

    assert "indexing failed" in caplog.text


def test_delete_product_removes_from_repository_and_index(service, index, repository):
    product = service.create_product("Tênis Velocity", "Tênis azul para corrida")

    service.delete_product(product.id)

    assert not index.contains(product.id)
    assert list(repository.load_all()) == []
    assert service.list_tags() == []


def test_delete_missing_product_does_not_call_repository(index, generator):
    repository = FailingRepository()
    service = CatalogService(index, repository, generator)

    with pytest.raises(ProductNotFoundError):
        service.delete_product(99)

    assert repository.delete_calls == 0


def test_delete_repository_failure_keeps_index(index, generator):
    repository = FailingRepository()
    service = CatalogService(index, repository, generator)
    product = service.create_product("Tênis Velocity", "Tênis azul para corrida")
    repository.fail_delete = True

    with pytest.raises(PersistenceError):
        service.delete_product(product.id)

    assert index.contains(product.id)


def test_get_missing_product_raises(service):
    with pytest.raises(ProductNotFoundError):
        service.get_product(1)


def test_search_ranks_by_matched_terms(service, generator):
    generator.tags = ("calcado", "corrida", "unissex", "azul", "tenis")
    shoe = service.create_product("Tênis Velocity", "Tênis azul para corrida")
    generator.tags = ("vestuario", "futebol", "masculino", "azul", "camiseta")
    shirt = service.create_product("Camiseta Azul", "Camiseta azul de futebol")

    hits = service.search("Tênis azul")

    assert [hit.product.id for hit in hits] == [shoe.id, shirt.id]
    assert hits[0].matched_tags == ("tenis", "azul")


@pytest.mark.parametrize("query", [None, "", "   "])
def test_search_blank_lists_everything_newest_first(service, query):
    first = service.create_product("Produto A", "Descrição do produto A")
    second = service.create_product("Produto B", "Descrição do produto B")

    assert [hit.product.id for hit in service.search(query)] == [second.id, first.id]


def test_search_with_only_stopwords_is_empty(service):
    service.create_product("Produto A", "Descrição do produto A")

    assert service.search("para") == []


def test_list_tags_has_counts_and_groups(service):
    service.create_product("Produto A", "Descrição do produto A")
    service.create_product("Produto B", "Descrição do produto B")

    tags = {tag: (count, group) for tag, count, group in service.list_tags()}

    assert tags["corrida"] == (2, TagGroup.SPORTS)
    assert tags["tenis"] == (2, TagGroup.FREE)


def test_load_index_rebuilds_from_repository(repository, generator):  # CA10
    for number in range(3):
        repository.insert(f"Produto {number}", "Descrição do produto", generator.tags)
    fresh_service = CatalogService(CatalogIndex(), repository, generator)

    assert fresh_service.load_index() == 3
    assert len(fresh_service.search("corrida")) == 3


def test_load_index_propagates_repository_failure(index, generator):
    class BrokenRepository:
        def load_all(self):
            raise PersistenceError("down")

    service = CatalogService(index, BrokenRepository(), generator)

    with pytest.raises(PersistenceError):
        service.load_index()


def test_stats(service):
    service.create_product("Produto A", "Descrição do produto A")

    assert service.stats() == (1, 5)
