import pytest

from app.utils.text_normalizer import normalize_tag, normalize_tags, tokenize_query


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Calçado Esportivo", ("calcado", "esportivo")),
        ("tênis de corrida", ("tenis", "corrida")),
        ("  AZUL!! ", ("azul",)),
        ("anti-derrapante", ("anti", "derrapante")),
        ("meia_calça 3/4", ("meia", "calca")),
        ("para", ()),
        ("de da do das dos com em um uma", ()),
        ("", ()),
        ("   ", ()),
        ("!!!", ()),
        ("a", ()),  # < 2 caracteres
        ("x" * 31, ()),  # > 30 caracteres
        ("x" * 30, ("x" * 30,)),
        ("tênis 42", ("tenis", "42")),
    ],
)
def test_normalize_tag(raw, expected):
    assert normalize_tag(raw) == expected


def test_normalize_tags_dedupes_preserving_order():
    assert normalize_tags(["azul", "Azul", "azul escuro"]) == ("azul", "escuro")


def test_normalize_tags_keeps_first_occurrence_order():
    assert normalize_tags(["verde", "azul", "verde claro", "AZUL"]) == ("verde", "azul", "claro")


def test_normalize_tags_empty_input():
    assert normalize_tags([]) == ()
    assert normalize_tags(["para", "!!"]) == ()


def test_normalize_tags_accepts_any_iterable():
    assert normalize_tags(raw for raw in ("Corrida", "corrida")) == ("corrida",)


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("para", ()),
        ("Tênis de CORRIDA azul", ("tenis", "corrida", "azul")),
        ("   ", ()),
    ],
)
def test_tokenize_query(query, expected):
    assert tokenize_query(query) == expected
