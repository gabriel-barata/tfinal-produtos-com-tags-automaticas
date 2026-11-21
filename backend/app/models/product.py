"""Entidade de domínio: produto do catálogo."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Product:
    """Produto já persistido.

    Imutável de propósito: o `CatalogIndex` guarda a mesma instância que é devolvida
    à API, então ninguém pode alterar o produto indexado por fora do índice.
    As tags são um `tuple` pelo mesmo motivo (e porque são geradas uma única vez).
    """

    id: int
    name: str
    description: str
    tags: tuple[str, ...]
    created_at: datetime
