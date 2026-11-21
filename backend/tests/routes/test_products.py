import pytest

from tests.routes.conftest import ADMIN_KEY

VALID_BODY = {"name": "Tênis Velocity", "description": "Tênis azul para corrida em asfalto"}
ADMIN = {"X-Admin-Key": ADMIN_KEY}


def create(client, generator=None, tags=None, **overrides):
    if generator is not None and tags is not None:
        generator.tags = tags
    return client.post("/api/products", json={**VALID_BODY, **overrides})


def test_create_returns_201_with_generated_tags(client, generator):  # CA1 (contrato)
    response = create(client)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Tênis Velocity"
    assert body["tags"] == list(generator.tags)
    assert "created_at" in body


def test_create_strips_whitespace(client):
    response = create(client, name="  Tênis Velocity  ")

    assert response.json()["name"] == "Tênis Velocity"


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": "T"},
        {"name": " T "},
        {"name": "x" * 121},
        {"description": "curta"},
        {"description": "x" * 1001},
        {"name": None},
    ],
)
def test_create_validation_errors_are_422(client, service, overrides):
    assert create(client, **overrides).status_code == 422
    assert len(service.search(None)) == 0


def test_create_accepts_boundary_sizes(client):
    assert create(client, name="ab", description="x" * 10).status_code == 201
    assert create(client, name="n" * 120, description="x" * 1000).status_code == 201


def test_create_missing_field_is_422(client):
    assert client.post("/api/products", json={"name": "Tênis"}).status_code == 422


def test_create_generator_failure_is_503_and_saves_nothing(client, generator):  # CA7
    generator.fail = True

    response = create(client)

    assert response.status_code == 503
    assert response.json() == {"detail": "Serviço de IA indisponível, tente novamente."}
    assert client.get("/api/products").json() == []


def test_search_finds_product_by_tag_ignoring_case_and_accents(client):  # CA2
    create(client)

    results = client.get("/api/products", params={"q": "Corrida"}).json()

    assert len(results) == 1
    assert results[0]["matched_tags"] == ["corrida"]
    assert results[0]["score"] == 1
    assert results[0]["product"]["name"] == "Tênis Velocity"


def test_search_ranks_by_score(client, generator):  # CA3
    create(client, generator, ("calcado", "corrida", "unissex", "azul", "tenis"))
    create(client, generator, ("vestuario", "futebol", "masculino", "azul", "camiseta"))

    results = client.get("/api/products", params={"q": "tênis azul"}).json()

    assert [r["product"]["id"] for r in results] == [1, 2]
    assert [r["score"] for r in results] == [2, 1]


def test_search_ties_newest_first(client):  # CA4
    create(client)
    create(client)

    results = client.get("/api/products", params={"q": "azul"}).json()

    assert [r["product"]["id"] for r in results] == [2, 1]


@pytest.mark.parametrize("params", [{}, {"q": ""}, {"q": "   "}])
def test_search_blank_lists_all_newest_first(client, params):  # CA5
    create(client)
    create(client)

    results = client.get("/api/products", params=params).json()

    assert [r["product"]["id"] for r in results] == [2, 1]
    assert [r["score"] for r in results] == [0, 0]
    assert [r["matched_tags"] for r in results] == [[], []]


@pytest.mark.parametrize("q", ["inexistente", "para"])
def test_search_without_matches_is_empty(client, q):  # CA6
    create(client)

    response = client.get("/api/products", params={"q": q})

    assert response.status_code == 200
    assert response.json() == []


def test_search_query_length_limit(client):
    assert client.get("/api/products", params={"q": "a" * 200}).status_code == 200
    assert client.get("/api/products", params={"q": "a" * 201}).status_code == 422


def test_get_product(client):
    create(client)

    response = client.get("/api/products/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Tênis Velocity"


def test_get_missing_product_is_404(client):
    response = client.get("/api/products/99")

    assert response.status_code == 404
    assert response.json() == {"detail": "Produto não encontrado."}


def test_get_product_with_non_numeric_id_is_422(client):
    assert client.get("/api/products/abc").status_code == 422


def test_delete_with_admin_key_removes_product_and_exclusive_tags(client, generator):  # CA8
    create(client, generator, ("calcado", "corrida", "unissex", "azul", "tenis"))
    create(client, generator, ("vestuario", "futebol", "masculino", "azul", "camiseta"))

    response = client.delete("/api/products/1", headers=ADMIN)

    assert response.status_code == 204
    assert response.content == b""
    assert [
        r["product"]["id"] for r in client.get("/api/products", params={"q": "azul"}).json()
    ] == [2]
    tags = {t["tag"] for t in client.get("/api/tags").json()}
    assert "tenis" not in tags
    assert "azul" in tags


@pytest.mark.parametrize("headers", [{}, {"X-Admin-Key": "wrong"}])
def test_delete_without_valid_key_is_401_and_changes_nothing(client, headers):  # CA9
    create(client)

    response = client.delete("/api/products/1", headers=headers)

    assert response.status_code == 401
    assert client.get("/api/products/1").status_code == 200


def test_delete_missing_product_is_404(client):
    assert client.delete("/api/products/99", headers=ADMIN).status_code == 404


def test_delete_unauthorized_does_not_reveal_whether_product_exists(client):
    assert client.delete("/api/products/99").status_code == 401
