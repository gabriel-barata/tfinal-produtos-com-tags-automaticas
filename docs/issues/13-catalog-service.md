# 13 · `CatalogService` (orquestração)

| Campo | Valor |
|---|---|
| Labels | `backend` |
| Tamanho | M |
| Depende de | 10, 11, 12 |
| Branch | `feat/13-catalog-service` |

## Objetivo
Casos de uso: cadastrar, obter, excluir, buscar, listar tags, rebuild no startup.

## Escopo
- [ ] `FakeTagGenerator` em `tests/conftest.py` (tags fixas ou configuráveis; modo "falhar")
- [ ] `app/services/catalog_service.py` com a interface da SPEC §11.3
- [ ] `create_product`: `top_free_tags(100)` → gerador (fora do lock) → `repository.insert` → `index.add`
- [ ] `delete_product`: checa índice → `repository.delete` → `index.remove`
- [ ] `search(query)`: vazio/espaços → `list_all`; senão `tokenize_query` → `index.search`
- [ ] `list_tags`: `tag_counts` + `group_of`
- [ ] `load_index`: `load_all` → `add`; retorna quantidade
- [ ] Log de erro se `index.add` falhar após `insert`

## Critérios de aceite
- [ ] Gerador falha → `TagGenerationError` propagada, repositório e índice intocados (CA7)
- [ ] Repositório falha no insert → nada indexado
- [ ] Repositório falha no delete → índice intacto
- [ ] Excluir id inexistente → `ProductNotFoundError` sem chamar o repositório
- [ ] `load_index` com 3 produtos no fake → busca retorna os 3 (CA10)

## Referências
SPEC §4.3, §11.3, §13
