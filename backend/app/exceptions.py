"""Exceções de domínio. Os handlers em `main.py` as traduzem para status HTTP."""


class ProductNotFoundError(Exception):
    """Nenhum produto com o id informado existe no catálogo."""

    def __init__(self, product_id: int) -> None:
        super().__init__(f"Produto {product_id} não encontrado")
        self.product_id = product_id
