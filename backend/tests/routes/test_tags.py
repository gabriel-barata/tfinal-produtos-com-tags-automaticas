def test_tags_empty_catalog(client):
    assert client.get("/api/tags").json() == []


def test_tags_have_correct_count_and_group(client, generator):  # CA12
    generator.tags = ("calcado", "corrida", "unissex", "azul", "tenis")
    client.post("/api/products", json={"name": "Tênis A", "description": "Descrição do tênis A"})
    client.post("/api/products", json={"name": "Tênis B", "description": "Descrição do tênis B"})

    tags = {t["tag"]: (t["count"], t["group"]) for t in client.get("/api/tags").json()}

    assert tags == {
        "calcado": (2, "department"),
        "corrida": (2, "sports"),
        "unissex": (2, "audience"),
        "azul": (2, "colors"),
        "tenis": (2, "free"),
    }


def test_tags_ordered_by_count_then_alphabetically(client, generator):
    generator.tags = ("calcado", "corrida", "unissex", "azul", "tenis")
    client.post("/api/products", json={"name": "Tênis A", "description": "Descrição do tênis A"})
    generator.tags = ("calcado", "futebol", "unissex", "preto", "chuteira")
    client.post("/api/products", json={"name": "Chuteira", "description": "Descrição da chuteira"})

    names = [t["tag"] for t in client.get("/api/tags").json()]

    assert names[:2] == ["calcado", "unissex"]
    assert names[2:] == sorted(names[2:])
