# 07 · `HashSet` (TDD)

| Campo | Valor |
|---|---|
| Labels | `estrutura-de-dados` |
| Tamanho | P |
| Depende de | 06 |
| Branch | `feat/07-hash-set` |

## Objetivo
Conjunto sem duplicatas, wrapper fino sobre `HashTable[K, None]`.

## Escopo
- [ ] Testes antes do código (oráculo `set`)
- [ ] `app/data_structures/hash_set.py`: `add`, `remove` (`KeyError`), `discard`, `__contains__`, `__len__`, `__iter__`, `__repr__`
- [ ] Docstrings pt-BR com Big-O

## Critérios de aceite
- [ ] Adicionar item repetido não altera `len`

## Referências
SPEC §5.5
