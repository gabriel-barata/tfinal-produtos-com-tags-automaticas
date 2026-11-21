"""Exceções de domínio. Os handlers em `main.py` as traduzem para status HTTP."""


class ProductNotFoundError(Exception):
    """Nenhum produto com o id informado existe no catálogo."""

    def __init__(self, product_id: int) -> None:
        super().__init__(f"Produto {product_id} não encontrado")
        self.product_id = product_id


class TagGenerationError(Exception):
    """A IA não devolveu tags válidas depois de todas as tentativas."""


class PersistenceError(Exception):
    """Falha ao falar com o banco de dados (conexão, SQL ou violação de restrição)."""
