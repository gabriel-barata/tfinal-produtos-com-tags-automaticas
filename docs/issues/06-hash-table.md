# 06 · `HashTable` (TDD)

| Campo | Valor |
|---|---|
| Labels | `estrutura-de-dados` |
| Tamanho | G |
| Depende de | 05 |
| Branch | `feat/06-hash-table` |

## Objetivo
Hash table com encadeamento separado e interface estilo `dict`: **a peça central dos 70% da nota**.

## Escopo
- [ ] Testes **antes** do código em `tests/data_structures/test_hash_table.py`
- [ ] `CollidingKey` (helper de teste) com `__hash__` constante e `__eq__` por valor
- [ ] Teste-oráculo: 10 000 operações aleatórias (seed fixa) de put/get/remove/contains aplicadas em `HashTable` e `dict`, comparando resultado e `len` a cada passo e o conteúdo final
- [ ] `app/data_structures/hash_table.py`: `[None] * capacity`, buckets `LinkedList` sob demanda, `hash(key) % capacity`, capacidade inicial 8, `MAX_LOAD_FACTOR = 0.75`, resize ×2 com rehash
- [ ] Métodos: `put`, `get(key, default=None)`, `remove`, `contains`, `keys`, `values`, `items`, dunders (`__setitem__`, `__getitem__`, `__delitem__`, `__contains__`, `__len__`, `__iter__`, `__repr__`), propriedades `capacity` e `load_factor`
- [ ] `initial_capacity < 1` → `ValueError`
- [ ] Docstrings pt-BR com Big-O

## Critérios de aceite
- [ ] Sobrescrever chave existente não altera `len`
- [ ] Resize só quando `len / capacity > 0.75`: com 6 itens a capacidade continua 8 (6/8 = 0,75); ao inserir o 7º passa a 16
- [ ] Nenhum item se perde em resize (verificado pelo oráculo)
- [ ] Com `CollidingKey`, todas as operações funcionam com todas as chaves num único bucket
- [ ] `__getitem__`/`remove`/`__delitem__` de chave ausente → `KeyError`

## Referências
SPEC §5.1, §5.2, §5.4, §16.1
