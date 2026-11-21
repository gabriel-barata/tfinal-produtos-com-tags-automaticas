# 11 · `ProductRepository` (Postgres via psycopg 3)

| Campo | Valor |
|---|---|
| Labels | `backend` |
| Tamanho | M |
| Depende de | 03, 08 |
| Branch | `feat/11-product-repository` |

## Objetivo
Persistência com SQL puro: `insert`, `delete`, `load_all`.

## Escopo
- [ ] `PersistenceError` em `app/exceptions.py`
- [ ] `app/repositories/product_repository.py`: `ProductRepository(pool: ConnectionPool)`; `insert(name, description, tags) -> Product` (`RETURNING id, created_at`); `delete(id) -> bool`; `load_all() -> Iterator[Product]` (`ORDER BY id`)
- [ ] Erros do psycopg encapsulados em `PersistenceError`
- [ ] Fábrica do pool (min 1, máx 3) a partir de `Settings.database_url`
- [ ] `InMemoryProductRepository` (fake) em `tests/conftest.py`, com a mesma interface

## Critérios de aceite
- [ ] `insert` devolve `Product` com `id` e `created_at` preenchidos e `tags` como `tuple`
- [ ] `delete` de id inexistente → `False`
- [ ] `load_all` devolve na ordem de id
- [ ] Violação do `CHECK` (nome curto) → `PersistenceError`

## Referências
SPEC §10
