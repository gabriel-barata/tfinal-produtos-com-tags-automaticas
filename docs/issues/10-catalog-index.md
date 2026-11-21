# 10 · `CatalogIndex` (índice em memória + busca OR ranqueada)

| Campo | Valor |
|---|---|
| Labels | `estrutura-de-dados`, `backend` |
| Tamanho | M |
| Depende de | 07, 08, 09 |
| Branch | `feat/10-catalog-index` |

## Objetivo
Índice que usa as estruturas próprias para armazenar produtos e responder buscas. **Sem I/O.**

## Escopo
- [ ] `app/exceptions.py` com `ProductNotFoundError` (demais exceções entram nos cards 11/12)
- [ ] `app/services/catalog_index.py`: `SearchHit(product, score, matched_tags)` frozen; `CatalogIndex` com `_products: HashTable[int, Product]`, `_tag_index: HashTable[str, HashSet[int]]`, `_lock: RLock`
- [ ] Métodos: `add`, `remove` (apaga a tag quando o set esvazia), `get`, `contains`, `search(terms)`, `list_all`, `tag_counts`, `top_free_tags(limit)`, `__len__`, `tag_total`
- [ ] `search` conforme SPEC §8.3: placar em `HashTable`, `sorted` por `(-score, -id)`
- [ ] Todos os métodos públicos sob o `RLock`
- [ ] Docstrings pt-BR com Big-O

## Critérios de aceite
- [ ] Produto A (`tenis`, `azul`) e B (`azul`): busca `("tenis", "azul")` → A (score 2), B (score 1)
- [ ] Empate → id maior primeiro
- [ ] Termo inexistente não pontua; só termos inexistentes → `[]`
- [ ] Remover o único produto com a tag `x` faz `x` sumir de `tag_counts`
- [ ] `top_free_tags` ignora tags do vocabulário base
- [ ] Nenhum `dict`/`set`/`list` como armazenamento (CT1)

## Referências
SPEC §8, §13
