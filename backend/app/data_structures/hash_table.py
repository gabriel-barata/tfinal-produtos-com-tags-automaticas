"""Tabela hash com encadeamento separado e interface estilo `dict`."""

from collections.abc import Iterator

from app.data_structures.linked_list import LinkedList


class HashTable[K, V]:
    """Tabela hash: array de buckets, cada bucket é uma `LinkedList` de pares chave/valor.

    A chave vira índice por `hash(chave) % capacidade`. Chaves diferentes que caem no
    mesmo bucket (colisão) ficam encadeadas na mesma lista. Quando
    `len / capacidade > MAX_LOAD_FACTOR`, o array dobra de tamanho e todos os pares são
    reinseridos (rehash), porque o `% capacidade` muda.

    Os buckets são criados sob demanda (`None` até a primeira inserção) para não gastar
    uma lista vazia por posição. A capacidade nunca diminui. Não é thread-safe, como o
    `dict`: quem compartilha a tabela entre threads precisa sincronizar por fora.
    """

    MAX_LOAD_FACTOR = 0.75

    def __init__(self, initial_capacity: int = 8) -> None:
        """Cria uma tabela vazia.

        Complexidade: O(capacidade inicial), para alocar o array de buckets.

        Raises:
            ValueError: se `initial_capacity < 1`.
        """
        if initial_capacity < 1:
            raise ValueError("initial_capacity deve ser >= 1")
        self._buckets: list[LinkedList | None] = [None] * initial_capacity
        self._size = 0

    # --- Operações principais ---

    def put(self, key: K, value: V) -> None:
        """Insere o par ou, se a chave já existe, troca o valor (o `len` não muda).

        Complexidade: média O(1) amortizado; pior caso O(n), quando todas as chaves
        colidem no mesmo bucket ou quando esta inserção dispara o resize.
        """
        index = self._bucket_index(key)
        bucket = self._buckets[index]
        if bucket is None:
            bucket = LinkedList()
            self._buckets[index] = bucket

        node = bucket.find_node(key)
        if node is not None:
            node.value = value  # sobrescrita não cria item novo, então nunca redimensiona
            return

        bucket.insert_front(key, value)
        self._size += 1
        if self._size / self.capacity > self.MAX_LOAD_FACTOR:
            self._resize(self.capacity * 2)

    def get(self, key: K, default: V | None = None) -> V | None:
        """Devolve o valor da chave, ou `default` se ela não existe.

        Complexidade: média O(1); pior caso O(n) (todas as chaves no mesmo bucket).
        """
        bucket = self._buckets[self._bucket_index(key)]
        if bucket is None:
            return default
        node = bucket.find_node(key)
        return default if node is None else node.value

    def remove(self, key: K) -> V:
        """Remove a chave e devolve o valor que ela guardava.

        Complexidade: média O(1); pior caso O(n).

        Raises:
            KeyError: se a chave não existe.
        """
        bucket = self._buckets[self._bucket_index(key)]
        if bucket is None:
            raise KeyError(key)
        value = bucket.remove(key)  # a própria lista levanta KeyError se ausente
        self._size -= 1
        return value

    def contains(self, key: K) -> bool:
        """Diz se a chave existe.

        Complexidade: média O(1); pior caso O(n).
        """
        bucket = self._buckets[self._bucket_index(key)]
        return bucket is not None and bucket.find_node(key) is not None

    # --- Iteração ---

    def keys(self) -> Iterator[K]:
        """Percorre as chaves (ordem não especificada).

        Complexidade: O(n + capacidade), pois visita todos os buckets.
        Não modifique a tabela durante a iteração.
        """
        for key, _ in self.items():
            yield key

    def values(self) -> Iterator[V]:
        """Percorre os valores (ordem não especificada).

        Complexidade: O(n + capacidade).
        """
        for _, value in self.items():
            yield value

    def items(self) -> Iterator[tuple[K, V]]:
        """Percorre os pares `(chave, valor)` (ordem não especificada).

        Complexidade: O(n + capacidade).
        """
        for bucket in self._buckets:
            if bucket is None:
                continue
            for node in bucket:
                yield node.key, node.value

    # --- Interface estilo dict ---

    def __setitem__(self, key: K, value: V) -> None:
        """`tabela[chave] = valor`; igual a `put`.

        Complexidade: média O(1) amortizado; pior caso O(n).
        """
        self.put(key, value)

    def __getitem__(self, key: K) -> V:
        """`tabela[chave]`; média O(1), pior caso O(n).

        Raises:
            KeyError: se a chave não existe.
        """
        bucket = self._buckets[self._bucket_index(key)]
        node = None if bucket is None else bucket.find_node(key)
        if node is None:
            raise KeyError(key)
        return node.value

    def __delitem__(self, key: K) -> None:
        """`del tabela[chave]`; igual a `remove`.

        Complexidade: média O(1); pior caso O(n).

        Raises:
            KeyError: se a chave não existe.
        """
        self.remove(key)

    def __contains__(self, key: object) -> bool:
        """`chave in tabela`; igual a `contains`.

        Complexidade: média O(1); pior caso O(n).
        """
        return self.contains(key)  # type: ignore[arg-type]

    def __len__(self) -> int:
        """Quantidade de pares. Complexidade: O(1) (contador mantido a cada operação)."""
        return self._size

    def __iter__(self) -> Iterator[K]:
        """Itera as chaves, como o `dict`; igual a `keys()`.

        Complexidade: O(n + capacidade) para percorrer tudo, em qualquer caso.
        """
        return self.keys()

    def __repr__(self) -> str:
        """Representação legível, ex.: `HashTable({'a': 1})`. Complexidade: O(n + capacidade)."""
        pairs = ", ".join(f"{key!r}: {value!r}" for key, value in self.items())
        return f"HashTable({{{pairs}}})"

    # --- Introspecção ---

    @property
    def capacity(self) -> int:
        """Quantidade de buckets do array. Complexidade: O(1)."""
        return len(self._buckets)

    @property
    def load_factor(self) -> float:
        """Fator de carga atual: `len / capacidade`. Complexidade: O(1)."""
        return self._size / self.capacity

    # --- Internos ---

    def _bucket_index(self, key: K) -> int:
        """Índice do bucket da chave. Em Python, `% capacidade` com capacidade > 0 é sempre >= 0."""
        return hash(key) % self.capacity

    def _resize(self, new_capacity: int) -> None:
        """Troca o array por um de `new_capacity` buckets e reinsere todos os pares.

        É preciso recalcular o índice de cada chave, pois ele depende da capacidade.
        Complexidade: O(n + capacidade).
        """
        old_buckets = self._buckets
        self._buckets = [None] * new_capacity
        for bucket in old_buckets:
            if bucket is None:
                continue
            for node in bucket:
                index = self._bucket_index(node.key)
                new_bucket = self._buckets[index]
                if new_bucket is None:
                    new_bucket = LinkedList()
                    self._buckets[index] = new_bucket
                new_bucket.insert_front(node.key, node.value)  # chaves já são únicas
