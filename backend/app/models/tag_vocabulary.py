"""Vocabulário base de tags, agrupado, e a cardinalidade de cada grupo."""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType


class TagGroup(StrEnum):
    """Grupos de tags. Os quatro primeiros são fechados; `FREE` é livre."""

    DEPARTMENT = "department"
    SPORTS = "sports"
    AUDIENCE = "audience"
    COLORS = "colors"
    FREE = "free"


# `MappingProxyType` torna o mapeamento somente leitura: é constante de configuração.
# O esporte "tênis" entra como `raquete`; `tenis` fica reservado ao calçado (cai em FREE).
BASE_VOCABULARY: Mapping[TagGroup, tuple[str, ...]] = MappingProxyType(
    {
        TagGroup.DEPARTMENT: ("calcado", "vestuario", "acessorio", "equipamento", "nutricao"),
        TagGroup.SPORTS: (
            "corrida",
            "futebol",
            "basquete",
            "volei",
            "natacao",
            "ciclismo",
            "musculacao",
            "yoga",
            "luta",
            "trilha",
            "raquete",
        ),
        TagGroup.AUDIENCE: ("masculino", "feminino", "unissex", "infantil"),
        TagGroup.COLORS: (
            "preto",
            "branco",
            "cinza",
            "azul",
            "vermelho",
            "verde",
            "amarelo",
            "laranja",
            "rosa",
            "roxo",
            "multicolor",
        ),
    }
)

# (mínimo, máximo) de tags por produto em cada grupo. Reutilizado pelo schema do Gemini
# e pela revalidação da resposta, para não duplicar os limites.
GROUP_CARDINALITY: Mapping[TagGroup, tuple[int, int]] = MappingProxyType(
    {
        TagGroup.DEPARTMENT: (1, 1),
        TagGroup.SPORTS: (1, 2),
        TagGroup.AUDIENCE: (1, 1),
        TagGroup.COLORS: (0, 2),
        TagGroup.FREE: (1, 4),
    }
)


def group_of(tag: str) -> TagGroup:
    """Devolve o grupo da tag; `FREE` se ela não pertence ao vocabulário base.

    Percorre no máximo 31 valores constantes, então o custo é O(1) na prática.
    """
    for group, values in BASE_VOCABULARY.items():
        if tag in values:
            return group
    return TagGroup.FREE
