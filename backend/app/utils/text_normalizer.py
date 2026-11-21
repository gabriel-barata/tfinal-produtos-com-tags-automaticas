"""Normalização de texto: a mesma pipeline serve para tags geradas e termos de busca.

Usar um único caminho garante que "Calçado" na busca case com "calcado" no índice.
"""

import re
import unicodedata
from collections.abc import Iterable

from app.data_structures.hash_set import HashSet

STOPWORDS = (
    "de",
    "da",
    "do",
    "das",
    "dos",
    "para",
    "com",
    "em",
    "e",
    "a",
    "o",
    "as",
    "os",
    "um",
    "uma",
)
MIN_WORD_LENGTH = 2
MAX_WORD_LENGTH = 30

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_tag(raw: str) -> tuple[str, ...]:
    """Normaliza um texto em zero ou mais palavras-tag.

    Etapas: minúsculas -> sem acentos -> não `[a-z0-9]` vira espaço -> quebra em
    palavras -> remove stopwords -> descarta palavras com < 2 ou > 30 caracteres.
    Pode devolver mais de uma palavra ("calçado esportivo") ou nenhuma ("para").
    """
    lowered = raw.lower().strip()
    # NFKD separa a letra do acento; descartar as marcas combinantes remove o acento.
    decomposed = unicodedata.normalize("NFKD", lowered)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    words = _NON_ALNUM.sub(" ", without_accents).split()
    return tuple(
        word
        for word in words
        if word not in STOPWORDS and MIN_WORD_LENGTH <= len(word) <= MAX_WORD_LENGTH
    )


def normalize_tags(raws: Iterable[str]) -> tuple[str, ...]:
    """Normaliza várias tags e remove duplicatas preservando a ordem da primeira ocorrência.

    A deduplicação usa `HashSet` (estrutura própria): a ordem vem da iteração de entrada,
    o conjunto só responde "já vi esta palavra?".
    """
    seen: HashSet[str] = HashSet()
    result: list[str] = []
    for raw in raws:
        for word in normalize_tag(raw):
            if word not in seen:
                seen.add(word)
                result.append(word)
    return tuple(result)


def tokenize_query(query: str) -> tuple[str, ...]:
    """Transforma o texto digitado na busca em termos normalizados (pode ser vazio)."""
    return normalize_tag(query)
