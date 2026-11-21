# 15 · Rotas de produtos e tags + schemas

| Campo | Valor |
|---|---|
| Labels | `backend` |
| Tamanho | M |
| Depende de | 14 |
| Branch | `feat/15-api-products-tags` |

## Objetivo
Expor o contrato HTTP da SPEC §9.

## Escopo
- [ ] Schemas (1 por arquivo): `product_create.py`, `product_response.py` (`from_entity`), `search_result.py`, `tag_count.py`
- [ ] `app/routes/products.py`: `POST /api/products` (201), `GET /api/products?q=` (`q` ≤ 200), `GET /api/products/{id}`, `DELETE /api/products/{id}` (204, `require_admin_key`)
- [ ] `app/routes/tags.py`: `GET /api/tags`
- [ ] Rotas finas: só convertem schema ↔ service
- [ ] Testes de rota com `TestClient` + fakes cobrindo CA1–CA9 e CA12

## Critérios de aceite
- [ ] Nome com 1 caractere → 422; descrição com 1001 → 422; `q` com 201 → 422
- [ ] Gerador fake falhando → 503 com mensagem pt-BR
- [ ] DELETE sem header / com chave errada → 401; com chave certa → 204 e produto some da busca
- [ ] `/api/tags` traz `group` correto para tags base e `free`

## Referências
SPEC §9, §20.1
