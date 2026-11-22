"""Lista simplesmente encadeada de pares chave/valor, usada como bucket da HashTable."""

from collections.abc import Iterator


class Node:
    """Nó da lista encadeada: guarda um par chave/valor e o ponteiro para o próximo."""

    __slots__ = ("key", "value", "next")

    def __init__(self, key: object, value: object, next: "Node | None" = None) -> None:
        """Cria o nó. Complexidade: O(1)."""
        self.key = key
        self.value = value
        self.next = next


class LinkedList:
    """Lista simplesmente encadeada de pares chave/valor.

    Só guarda o ponteiro para a cabeça e o tamanho; não usa nenhuma coleção
    embutida do Python. O tamanho é mantido em um contador para que `len()`
    seja O(1), já que a HashTable consulta o tamanho dos buckets com frequência.
    """

    def __init__(self) -> None:
        """Cria a lista vazia. Complexidade: O(1)."""
        self.head: Node | None = None
        self._size = 0

    def insert_front(self, key: object, value: object) -> None:
        """Insere um novo par no início da lista.

        Não verifica duplicatas: quem precisa de chaves únicas (a HashTable)
        deve chamar `find_node` antes. Inserir na cabeça evita percorrer a lista.

        Complexidade: O(1) no caso médio e no pior caso.
        """
        self.head = Node(key, value, self.head)
        self._size += 1

    def find_node(self, key: object) -> Node | None:
        """Procura o nó da chave, comparando com `==`.

        Devolve o próprio nó (e não só o valor) para o chamador poder atualizar
        `node.value` sem reinserir. Devolve `None` se a chave não existe.

        Complexidade: média O(k) e pior caso O(k), com k = tamanho da lista
        (na HashTable, k é pequeno em média).
        """
        node = self.head
        while node is not None:
            if node.key == key:
                return node
            node = node.next
        return None

    def remove(self, key: object) -> object:
        """Remove o nó da chave e devolve o valor que ele guardava.

        Complexidade: média O(k) e pior caso O(k), com k = tamanho da lista.

        Raises:
            KeyError: se a chave não está na lista (a lista fica intacta).
        """
        previous: Node | None = None
        node = self.head
        while node is not None:
            if node.key == key:
                if previous is None:
                    self.head = node.next  # removendo a cabeça
                else:
                    previous.next = node.next  # religa o anterior ao seguinte
                self._size -= 1
                return node.value
            previous = node
            node = node.next
        raise KeyError(key)

    def __iter__(self) -> Iterator[Node]:
        """Percorre os nós, da cabeça até a cauda.

        Complexidade: O(k) para percorrer tudo; cada passo é O(1).
        Não modifique a lista durante a iteração.
        """
        node = self.head
        while node is not None:
            yield node
            node = node.next

    def __len__(self) -> int:
        """Quantidade de nós. Complexidade: O(1) (contador mantido a cada operação)."""
        return self._size

    def __bool__(self) -> bool:
        """`True` se a lista tem ao menos um nó. Complexidade: O(1)."""
        return self._size > 0

    def __repr__(self) -> str:
        """Representação legível, ex.: `LinkedList(('b', 2) -> ('a', 1))`. Complexidade: O(k)."""
        if self.head is None:
            return "LinkedList()"
        pairs = " -> ".join(f"({node.key!r}, {node.value!r})" for node in self)
        return f"LinkedList({pairs})"
