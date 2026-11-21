"""Persistência dos produtos em Postgres (psycopg 3, SQL puro).

O banco é só armazenamento durável: toda busca é respondida pelo `CatalogIndex` em memória.
"""

from collections.abc import Iterator

import psycopg
from psycopg_pool import ConnectionPool

from app.exceptions import PersistenceError
from app.models.product import Product

POOL_MIN_SIZE = 1
POOL_MAX_SIZE = 3
POOL_OPEN_TIMEOUT_S = 10.0


def create_pool(database_url: str) -> ConnectionPool:
    """Abre o pool de conexões e espera a primeira conexão ficar pronta.

    Esperar na criação faz o startup falhar rápido (fail fast) se o banco estiver
    inacessível, em vez de descobrir só na primeira requisição.

    Raises:
        PersistenceError: se não for possível conectar dentro do prazo.
    """
    pool = ConnectionPool(database_url, min_size=POOL_MIN_SIZE, max_size=POOL_MAX_SIZE, open=False)
    try:
        pool.open(wait=True, timeout=POOL_OPEN_TIMEOUT_S)
    except psycopg.Error as exc:
        pool.close()
        raise PersistenceError("Não foi possível conectar ao banco de dados") from exc
    return pool


class ProductRepository:
    """CRUD mínimo da tabela `products`: `insert`, `delete` e `load_all`."""

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def insert(self, name: str, description: str, tags: tuple[str, ...]) -> Product:
        """Grava um produto e devolve-o com `id` e `created_at` gerados pelo banco.

        Complexidade: uma ida ao banco; O(t) no número de tags.

        Raises:
            PersistenceError: falha de conexão ou violação de restrição (ex.: CHECK de tamanho).
        """
        try:
            with self._pool.connection() as conn:
                row = conn.execute(
                    "INSERT INTO products (name, description, tags) VALUES (%s, %s, %s) "
                    "RETURNING id, created_at",
                    (name, description, list(tags)),  # psycopg adapta list -> text[]
                ).fetchone()
        except psycopg.Error as exc:
            raise PersistenceError("Falha ao salvar o produto") from exc
        # RETURNING sempre devolve uma linha quando o INSERT tem sucesso.
        assert row is not None
        return Product(id=row[0], name=name, description=description, tags=tags, created_at=row[1])

    def delete(self, product_id: int) -> bool:
        """Remove o produto; devolve `False` se o id não existia.

        Complexidade: uma ida ao banco; O(log n) pela chave primária.

        Raises:
            PersistenceError: falha de conexão ou SQL.
        """
        try:
            with self._pool.connection() as conn:
                cursor = conn.execute("DELETE FROM products WHERE id = %s", (product_id,))
                return cursor.rowcount > 0
        except psycopg.Error as exc:
            raise PersistenceError("Falha ao excluir o produto") from exc

    def load_all(self) -> Iterator[Product]:
        """Devolve todos os produtos em ordem de id (usado para reconstruir o índice no startup).

        Complexidade: O(n) no número de produtos.

        Raises:
            PersistenceError: falha de conexão ou SQL (levantada ao iterar).
        """
        try:
            with self._pool.connection() as conn:
                cursor = conn.execute(
                    "SELECT id, name, description, tags, created_at FROM products ORDER BY id"
                )
                for row in cursor:
                    yield Product(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        tags=tuple(row[3]),
                        created_at=row[4],
                    )
        except psycopg.Error as exc:
            raise PersistenceError("Falha ao carregar os produtos") from exc
