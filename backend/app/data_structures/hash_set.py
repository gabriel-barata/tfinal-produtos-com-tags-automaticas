"""Conjunto sem duplicatas, construído sobre a HashTable."""

from collections.abc import Iterator

from app.data_structures.hash_table import HashTable


class HashSet[K]:
    """Conjunto de itens únicos: wrapper fino sobre `HashTable[K, None]`.

    Só as chaves importam; o valor guardado é sempre `None`. Reaproveitar a HashTable
    mantém colisão e resize em um único lugar. Não é thread-safe, como o `set`.
    """

    def __init__(self) -> None:
        self._table: HashTable[K, None] = HashTable()

    def add(self, item: K) -> None:
        """Adiciona o item; se já existe, não faz nada (o `len` não muda).

        Complexidade: média O(1) amortizado; pior caso O(n).
        """
        self._table.put(item, None)

    def remove(self, item: K) -> None:
        """Remove o item.

        Complexidade: média O(1); pior caso O(n).

        Raises:
            KeyError: se o item não está no conjunto.
        """
        self._table.remove(item)

    def discard(self, item: K) -> None:
        """Remove o item se existir; silencioso se ausente.

        Complexidade: média O(1); pior caso O(n).
        """
        if item in self._table:
            self._table.remove(item)

    def __contains__(self, item: object) -> bool:
        """`item in conjunto`. Complexidade: média O(1); pior caso O(n)."""
        return item in self._table

    def __len__(self) -> int:
        """Quantidade de itens. Complexidade: O(1)."""
        return len(self._table)

    def __iter__(self) -> Iterator[K]:
        """Percorre os itens (ordem não especificada).

        Complexidade: O(n + capacidade). Não modifique o conjunto durante a iteração.
        """
        return iter(self._table)

    def __repr__(self) -> str:
        """Representação legível, ex.: `HashSet({1, 2})`. Complexidade: O(n + capacidade)."""
        if len(self) == 0:
            return "HashSet()"
        return f"HashSet({{{', '.join(repr(item) for item in self)}}})"
