# 05 · `Node` + `LinkedList` (TDD)

| Campo | Valor |
|---|---|
| Labels | `estrutura-de-dados` |
| Tamanho | M |
| Depende de | 02 |
| Branch | `feat/05-linked-list` |

## Objetivo
Lista simplesmente encadeada de pares chave/valor, usada como bucket da `HashTable`.

## Escopo
- [ ] Testes **antes** do código em `tests/data_structures/test_linked_list.py`
- [ ] `app/data_structures/linked_list.py`: `Node(key, value, next)`, `LinkedList` com `insert_front`, `find_node`, `remove` (devolve valor; `KeyError` se ausente), `__iter__` (nós), `__len__` O(1), `__bool__`, `__repr__`
- [ ] Docstrings pt-BR com Big-O (média/pior) em todo método público
- [ ] Nenhum `list`/`dict`/`append` interno

## Critérios de aceite
- [ ] Remoção testada na cabeça, no meio, no fim, em lista de 1 elemento e para chave ausente
- [ ] `len` correto após qualquer sequência de operações

## Referências
SPEC §5.3, §5.6, §2.2
