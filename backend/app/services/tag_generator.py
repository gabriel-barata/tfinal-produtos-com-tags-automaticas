"""Geração de tags com o Gemini: structured output, revalidação, normalização e retry."""

import logging
from collections.abc import Sequence

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError, field_validator

from app.exceptions import TagGenerationError
from app.models.tag_vocabulary import BASE_VOCABULARY, GROUP_CARDINALITY, TagGroup
from app.utils.text_normalizer import normalize_tags

logger = logging.getLogger(__name__)

TEMPERATURE = 0.2
MAX_FREE_TAGS = GROUP_CARDINALITY[TagGroup.FREE][1]

_SYSTEM_INSTRUCTION = """\
Você classifica produtos de uma loja brasileira de artigos esportivos.
Gere tags para indexar o produto na busca da loja.

Regras:
1. department, sports, audience e colors: use SOMENTE os valores permitidos no schema.
2. colors: lista vazia se o produto não tiver cor definida (ex.: suplementos).
3. free_tags: de 1 a 4 tags, cada uma com UMA palavra, em português, minúsculas,
   no singular e genérica. A primeira deve ser o tipo do produto
   (ex.: tenis, bola, camiseta, shorts, luva, whey, garrafa).
4. Nunca use frases: "tênis de corrida" vira "tenis" (e "corrida" já está em sports).
5. Não repita em free_tags valores já escolhidos nos outros campos.
6. Quando uma destas tags existentes descrever o produto, reutilize-a em vez de criar sinônimo:
   {existing_free_tags}"""


def build_response_schema() -> dict:
    """Monta o schema JSON do structured output a partir de `BASE_VOCABULARY`.

    Os enums e os limites min/max vêm das constantes do domínio, sem duplicar listas.
    """

    def closed_group(group: TagGroup) -> dict:
        return {"type": "string", "enum": list(BASE_VOCABULARY[group])}

    def array_of(item: dict, group: TagGroup) -> dict:
        low, high = GROUP_CARDINALITY[group]
        return {"type": "array", "items": item, "minItems": low, "maxItems": high}

    return {
        "type": "object",
        "properties": {
            "department": closed_group(TagGroup.DEPARTMENT),
            "sports": array_of(closed_group(TagGroup.SPORTS), TagGroup.SPORTS),
            "audience": closed_group(TagGroup.AUDIENCE),
            "colors": array_of(closed_group(TagGroup.COLORS), TagGroup.COLORS),
            "free_tags": array_of({"type": "string"}, TagGroup.FREE),
        },
        "required": ["department", "sports", "audience", "colors", "free_tags"],
    }


def build_prompt(name: str, description: str, existing_free_tags: Sequence[str]) -> tuple[str, str]:
    """Devolve `(system_instruction, conteúdo_do_usuário)`. Função pura, testável sem rede.

    `existing_free_tags` (vazio no primeiro cadastro) incentiva reaproveitar tags já usadas
    em vez de criar sinônimos, o que mantém o índice coeso.
    """
    system = _SYSTEM_INSTRUCTION.format(existing_free_tags=", ".join(existing_free_tags))
    content = f"Nome: {name}\nDescrição: {description}"
    return system, content


# Nome do campo da resposta -> grupo do vocabulário.
_GROUP_BY_FIELD = {
    "department": TagGroup.DEPARTMENT,
    "sports": TagGroup.SPORTS,
    "audience": TagGroup.AUDIENCE,
    "colors": TagGroup.COLORS,
    "free_tags": TagGroup.FREE,
}


class _GeneratedTags(BaseModel):
    """Revalida a resposta: o schema do provedor não é garantia absoluta."""

    department: str
    sports: list[str]
    audience: str
    colors: list[str]
    free_tags: list[str]

    @field_validator("department", "audience", "sports", "colors")
    @classmethod
    def _only_allowed_values(cls, value: str | list[str], info) -> str | list[str]:
        allowed = BASE_VOCABULARY[_GROUP_BY_FIELD[info.field_name]]
        items = [value] if isinstance(value, str) else value
        for item in items:
            if item not in allowed:
                raise ValueError(f"{item!r} não pertence ao grupo {info.field_name}")
        return value

    @field_validator("sports", "colors", "free_tags")
    @classmethod
    def _within_cardinality(cls, value: list[str], info) -> list[str]:
        low, high = GROUP_CARDINALITY[_GROUP_BY_FIELD[info.field_name]]
        if not low <= len(value) <= high:
            raise ValueError(f"{info.field_name} deve ter entre {low} e {high} itens")
        return value


class GeminiTagGenerator:
    """Gera as tags de um produto chamando o Gemini (somente no cadastro, nunca na busca)."""

    def __init__(
        self,
        client: genai.Client,
        model: str,
        max_attempts: int = 2,
        timeout_s: float = 15,
    ) -> None:
        self._client = client
        self._model = model
        self._max_attempts = max_attempts
        self._timeout_s = timeout_s

    def generate(
        self, name: str, description: str, existing_free_tags: Sequence[str]
    ) -> tuple[str, ...]:
        """Devolve as tags finais (normalizadas, sem duplicatas) do produto.

        Tenta até `max_attempts` vezes; qualquer erro (rede, cota, JSON inválido, validação)
        conta como tentativa falha. Não há fallback por palavras-chave (decisão D02).

        Raises:
            TagGenerationError: se todas as tentativas falharem.
        """
        system, content = build_prompt(name, description, existing_free_tags)
        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=TEMPERATURE,
            response_mime_type="application/json",
            response_schema=build_response_schema(),
            http_options=types.HttpOptions(timeout=int(self._timeout_s * 1000)),  # em ms
        )
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model, contents=content, config=config
                )
                return self._postprocess(response.text)
            except Exception as exc:  # qualquer falha do provedor vale retry
                last_error = exc
                logger.warning(
                    "Tentativa %d/%d de gerar tags falhou: %s", attempt, self._max_attempts, exc
                )
        raise TagGenerationError("Não foi possível gerar tags para o produto") from last_error

    @staticmethod
    def _postprocess(raw_json: str | None) -> tuple[str, ...]:
        """Valida o JSON e produz a tupla final de tags (SPEC §7.4)."""
        if not raw_json:
            raise ValueError("resposta vazia")
        try:
            data = _GeneratedTags.model_validate_json(raw_json)
        except ValidationError as exc:
            raise ValueError(f"resposta fora do contrato: {exc}") from exc

        # Normaliza o bloco fechado primeiro: ele é sempre preservado inteiro.
        base = normalize_tags([data.department, *data.sports, data.audience, *data.colors])
        # Normalizar de novo com as livres evita duplicar tags que já estão no bloco fechado
        # e quebra compostas ("calçado esportivo") antes de aplicar o limite de 4 livres.
        combined = normalize_tags([*base, *data.free_tags])
        tags = base + combined[len(base) :][:MAX_FREE_TAGS]

        if data.department not in tags:
            raise ValueError("resposta sem department")
        return tags
