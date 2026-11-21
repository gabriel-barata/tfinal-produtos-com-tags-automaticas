"""Índice em memória do catálogo: produtos por id + índice invertido tag -> ids."""

from dataclasses import dataclass
from threading import RLock

from app.data_structures.hash_set import HashSet
from app.data_structures.hash_table import HashTable
from app.exceptions import ProductNotFoundError
from app.models.product import Product
from app.models.tag_vocabulary import TagGroup, group_of


@dataclass(frozen=True)
class SearchHit:
    """Um resultado de busca: o produto, quantos termos casaram e quais foram."""

    product: Product
    score: int
    matched_tags: tuple[str, ...]


class CatalogIndex:
    """Responde toda leitura e busca do catálogo, sem tocar em banco ou rede (sem I/O).

    Guarda dois índices, ambos com as estruturas próprias do projeto:
    - `_products`: id -> produto (acesso direto por id);
    - `_tag_index`: tag -> conjunto de ids (índice invertido: a busca vai da tag aos
      produtos sem varrer o catálogo).

    Todos os métodos públicos adquirem o `RLock`, pois o FastAPI atende requisições em
    threads diferentes e `HashTable`/`HashSet` não são thread-safe. É `RLock` (e não
    `Lock`) para que um método público possa chamar outro sem travar a si mesmo.

    Notação de complexidade: t = tags do produto, q = termos da busca, m = soma dos ids
    encontrados nas tags buscadas, r = resultados, n = produtos, T = tags distintas.
    As complexidades são médias, herdadas da `HashTable`.
    """

    def __init__(self) -> None:
        self._products: HashTable[int, Product] = HashTable()
        self._tag_index: HashTable[str, HashSet[int]] = HashTable()
        self._lock = RLock()

    def add(self, product: Product) -> None:
        """Indexa o produto: guarda por id e registra o id em cada uma de suas tags.

        Complexidade: O(t).
        """
        with self._lock:
            self._products.put(product.id, product)
            for tag in product.tags:
                ids = self._tag_index.get(tag)
                if ids is None:
                    ids = HashSet()
                    self._tag_index.put(tag, ids)
                ids.add(product.id)

    def remove(self, product_id: int) -> Product:
        """Remove o produto e devolve o que foi removido.

        Tira o id de cada tag e apaga a tag quando o conjunto esvazia, para que tags
        sem produto não apareçam em `tag_counts` nem inflem `tag_total`.

        Complexidade: O(t).

        Raises:
            ProductNotFoundError: se o id não está no índice.
        """
        with self._lock:
            product = self.get(product_id)
            self._products.remove(product_id)
            for tag in product.tags:
                ids = self._tag_index.get(tag)
                if ids is None:
                    continue
                ids.discard(product_id)
                if len(ids) == 0:
                    self._tag_index.remove(tag)
            return product

    def get(self, product_id: int) -> Product:
        """Devolve o produto pelo id.

        Complexidade: O(1).

        Raises:
            ProductNotFoundError: se o id não está no índice.
        """
        with self._lock:
            product = self._products.get(product_id)
            if product is None:
                raise ProductNotFoundError(product_id)
            return product

    def contains(self, product_id: int) -> bool:
        """Diz se o id está indexado. Complexidade: O(1)."""
        with self._lock:
            return product_id in self._products

    def search(self, terms: tuple[str, ...]) -> list[SearchHit]:
        """Busca OR ranqueada: cada termo que casa com uma tag do produto vale 1 ponto.

        Termo sem produto não pontua. Ordena por mais termos casados e, no empate, pelo
        maior id (mais recente). O placar é uma `HashTable` própria; o `sorted` final só
        monta a resposta. Os termos já devem vir normalizados (`tokenize_query`).

        Complexidade: O(q + m + r log r).
        """
        with self._lock:
            scores: HashTable[int, int] = HashTable()
            matched: HashTable[int, tuple[str, ...]] = HashTable()
            for term in terms:
                ids = self._tag_index.get(term)
                if ids is None:
                    continue
                for product_id in ids:
                    scores[product_id] = scores.get(product_id, 0) + 1
                    matched[product_id] = matched.get(product_id, ()) + (term,)
            hits = (
                SearchHit(self._products[product_id], score, matched[product_id])
                for product_id, score in scores.items()
            )
            return sorted(hits, key=lambda hit: (-hit.score, -hit.product.id))

    def list_all(self) -> list[SearchHit]:
        """Todos os produtos, mais recentes (maior id) primeiro, com `score=0`.

        Complexidade: O(n log n).
        """
        with self._lock:
            hits = (SearchHit(product, 0, ()) for product in self._products.values())
            return sorted(hits, key=lambda hit: -hit.product.id)

    def tag_counts(self) -> list[tuple[str, int]]:
        """Pares `(tag, nº de produtos)`, por contagem decrescente e depois alfabética.

        Complexidade: O(T log T).
        """
        with self._lock:
            pairs = ((tag, len(ids)) for tag, ids in self._tag_index.items())
            return sorted(pairs, key=lambda pair: (-pair[1], pair[0]))

    def top_free_tags(self, limit: int) -> tuple[str, ...]:
        """Até `limit` tags livres (fora do vocabulário base) mais usadas, mesma ordem de
        `tag_counts`. Alimenta o prompt da IA para ela reaproveitar tags existentes.

        Complexidade: O(T log T).
        """
        with self._lock:
            free = [
                (tag, count) for tag, count in self.tag_counts() if group_of(tag) == TagGroup.FREE
            ]
            return tuple(tag for tag, _ in free[:limit])

    def __len__(self) -> int:
        """Quantidade de produtos indexados. Complexidade: O(1)."""
        with self._lock:
            return len(self._products)

    @property
    def tag_total(self) -> int:
        """Quantidade de tags distintas no índice. Complexidade: O(1)."""
        with self._lock:
            return len(self._tag_index)
