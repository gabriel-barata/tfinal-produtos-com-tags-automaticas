"""Testes do GeminiTagGenerator com client mockado (sem rede)."""

import json
from types import SimpleNamespace

import pytest

from app.exceptions import TagGenerationError
from app.models.tag_vocabulary import BASE_VOCABULARY
from app.services.tag_generator import GeminiTagGenerator, build_prompt, build_response_schema


class FakeModels:
    """Devolve respostas roteirizadas; uma exceção na fila é lançada em vez de devolvida."""

    def __init__(self, *outcomes: object) -> None:
        self._outcomes = list(outcomes)
        self.calls: list[dict] = []

    def generate_content(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return SimpleNamespace(text=outcome)


def make_generator(*outcomes: object) -> tuple[GeminiTagGenerator, FakeModels]:
    models = FakeModels(*outcomes)
    client = SimpleNamespace(models=models)
    return GeminiTagGenerator(client, model="fake-model"), models  # type: ignore[arg-type]


def payload(**overrides: object) -> str:
    data = {
        "department": "calcado",
        "sports": ["corrida"],
        "audience": "unissex",
        "colors": ["azul"],
        "free_tags": ["tenis", "asfalto", "amortecimento"],
    }
    data.update(overrides)
    return json.dumps(data)


def test_spec_example_produces_expected_tags() -> None:
    generator, _ = make_generator(payload())
    tags = generator.generate("Tênis Velocity", "Tênis azul para corrida em asfalto", ())
    assert tags == ("calcado", "corrida", "unissex", "azul", "tenis", "asfalto", "amortecimento")


def test_invalid_json_then_success_retries() -> None:
    generator, models = make_generator("isto não é json", payload())
    tags = generator.generate("Tênis", "Tênis azul para corrida", ())
    assert tags[0] == "calcado"
    assert len(models.calls) == 2


def test_two_failures_raise_tag_generation_error() -> None:
    generator, models = make_generator(RuntimeError("cota"), payload(department="inexistente"))
    with pytest.raises(TagGenerationError):
        generator.generate("Tênis", "Tênis azul para corrida", ())
    assert len(models.calls) == 2


def test_empty_response_is_a_failed_attempt() -> None:
    generator, _ = make_generator(None, "")
    with pytest.raises(TagGenerationError):
        generator.generate("Tênis", "Tênis azul para corrida", ())


def test_free_tags_are_truncated_to_four_after_splitting_compounds() -> None:
    raw = payload(free_tags=["calçado esportivo", "leve", "macio", "barato"])
    generator, _ = make_generator(raw)
    tags = generator.generate("Tênis", "Tênis azul para corrida", ())
    # "calçado" duplica o department e sai na deduplicação; sobram 4 livres a partir de "esportivo".
    assert tags[4:] == ("esportivo", "leve", "macio", "barato")


def test_free_tag_repeating_closed_value_is_deduplicated() -> None:
    generator, _ = make_generator(payload(free_tags=["azul", "tenis"]))
    tags = generator.generate("Tênis", "Tênis azul para corrida", ())
    assert tags == ("calcado", "corrida", "unissex", "azul", "tenis")


def test_free_tags_out_of_range_are_rejected() -> None:
    generator, _ = make_generator(payload(free_tags=[]), payload(free_tags=list("abcde")))
    with pytest.raises(TagGenerationError):
        generator.generate("Tênis", "Tênis azul para corrida", ())


def test_request_uses_structured_output_and_low_temperature() -> None:
    generator, models = make_generator(payload())
    generator.generate("Tênis", "Tênis azul para corrida", ())
    config = models.calls[0]["config"]
    assert config.temperature == 0.2
    assert config.response_mime_type == "application/json"
    assert config.http_options.timeout == 15000


def test_schema_contains_all_31_enum_values() -> None:
    props = build_response_schema()["properties"]
    values = {
        *props["department"]["enum"],
        *props["sports"]["items"]["enum"],
        *props["audience"]["enum"],
        *props["colors"]["items"]["enum"],
    }
    assert len(values) == 31
    assert values == {tag for tags in BASE_VOCABULARY.values() for tag in tags}
    assert props["sports"]["minItems"] == 1 and props["sports"]["maxItems"] == 2
    assert props["colors"]["minItems"] == 0
    assert props["free_tags"]["maxItems"] == 4


def test_prompt_includes_existing_free_tags_and_product() -> None:
    system, content = build_prompt("Bola X", "Bola de futebol oficial", ("bola", "chuteira"))
    assert "bola, chuteira" in system
    assert "Nome: Bola X" in content and "Bola de futebol oficial" in content


def test_prompt_with_no_existing_tags_has_empty_list() -> None:
    system, _ = build_prompt("Bola X", "Bola de futebol oficial", ())
    assert system.rstrip().endswith("sinônimo:")
    assert "{existing_free_tags}" not in system
