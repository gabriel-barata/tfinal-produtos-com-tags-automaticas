"""Casos de uso do catálogo: orquestra gerador de tags, repositório e índice em memória."""

import logging

from app.models.product import Product
from app.models.tag_vocabulary import TagGroup, group_of
from app.repositories.product_repository import ProductRepository
from app.services.catalog_index import CatalogIndex, SearchHit
from app.services.tag_generator import GeminiTagGenerator
from app.utils.text_normalizer import tokenize_query

logger = logging.getLogger(__name__)

# Quantas tags livres já existentes vão no prompt para a IA reaproveitar (SPEC §4.3).
EXISTING_TAGS_IN_PROMPT = 100


class CatalogService:
    """Único ponto que conhece gerador de tags, repositório e índice.

    Os três são injetados (duck typing): os testes passam fakes em vez de Gemini e Postgres.
    A consistência entre banco e índice depende da ordem das operações (SPEC §13): o banco
    é gravado primeiro, então uma falha dele nunca deixa algo no índice.
    """

    def __init__(
        self,
        index: CatalogIndex,
        repository: ProductRepository,
        tag_generator: GeminiTagGenerator,
    ) -> None:
        self._index = index
        self._repository = repository
        self._tag_generator = tag_generator

    def load_index(self) -> int:
        """Reconstrói o índice a partir do banco (startup) e devolve quantos produtos carregou.

        Complexidade: O(n * t), com n produtos e t tags por produto.

        Raises:
            PersistenceError: se o banco falhar; o startup deve abortar (fail fast).
        """
        count = 0
        for product in self._repository.load_all():
            self._index.add(product)
            count += 1
        return count

    def create_product(self, name: str, description: str) -> Product:
        """Gera as tags com a IA, grava no banco e indexa. Devolve o produto salvo.

        A chamada à IA (lenta) acontece fora de qualquer lock do índice, para não bloquear
        buscas enquanto o Gemini responde.

        Raises:
            TagGenerationError: IA indisponível ou resposta inválida; nada é salvo.
            PersistenceError: falha no banco; nada é indexado.
        """
        existing_tags = self._index.top_free_tags(EXISTING_TAGS_IN_PROMPT)
        tags = self._tag_generator.generate(name, description, existing_tags)
        product = self._repository.insert(name, description, tags)
        try:
            self._index.add(product)
        except Exception:
            # Improvável, mas deixaria banco e índice divergentes até o próximo restart
            # (que reconstrói o índice). Aceito no MVP; só registramos para diagnóstico.
            logger.exception("Product %d saved but indexing failed", product.id)
            raise
        return product

    def get_product(self, product_id: int) -> Product:
        """Devolve o produto pelo id.

        Raises:
            ProductNotFoundError: se não existir.
        """
        return self._index.get(product_id)

    def delete_product(self, product_id: int) -> None:
        """Exclui do banco e do índice.

        A existência é checada no índice antes de qualquer ida ao banco, e o índice só é
        alterado depois do `DELETE` bem-sucedido: falha no banco deixa o índice intacto.

        Raises:
            ProductNotFoundError: se o id não existir.
            PersistenceError: falha no banco; o produto continua indexado.
        """
        # `get` já levanta ProductNotFoundError.
        self._index.get(product_id)
        self._repository.delete(product_id)
        self._index.remove(product_id)

    def search(self, query: str | None) -> list[SearchHit]:
        """Busca ranqueada por tags; consulta vazia ou só com espaços lista tudo."""
        if query is None or not query.strip():
            return self._index.list_all()
        return self._index.search(tokenize_query(query))

    def list_tags(self) -> list[tuple[str, int, TagGroup]]:
        """Todas as tags do índice como `(tag, nº de produtos, grupo)`."""
        return [(tag, count, group_of(tag)) for tag, count in self._index.tag_counts()]

    def stats(self) -> tuple[int, int]:
        """`(nº de produtos, nº de tags distintas)`, usado pelo `/health`."""
        return len(self._index), self._index.tag_total
