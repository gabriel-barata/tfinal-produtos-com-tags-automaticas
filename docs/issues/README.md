# Issues — índice

Cada arquivo `NN-slug.md` vira 1 card no Trello e 1 PR (exceto cards `manual`). Fonte da verdade: [`../SPEC.md`](../SPEC.md).

## Convenções

| Item | Regra |
|---|---|
| Tamanho | **P** ≤ 30 min · **M** 30–90 min · **G** > 90 min |
| Branch | `<tipo>/<NN>-slug`, conforme o campo "Branch" do card |
| Pronto (DoD) | critérios de aceite marcados + CI verde + squash merge na `main` |

## Labels

| Label | Uso |
|---|---|
| `estrutura-de-dados` | 70% da nota: revisão extra (sem `dict`/`list` como armazenamento) |
| `backend` | código Python fora das estruturas |
| `ia` | integração com o Gemini |
| `frontend` | HTML/CSS/JS |
| `infra` | tooling, Docker, CI, deploy |
| `docs` | README e entrega |
| `manual` | executado fora do código (painéis web) |

## Cards

| # | Card | Labels | Tam. | Depende de |
|---|---|---|---|---|
| 01 | [Bootstrap do repositório](01-repo-bootstrap.md) | infra | P | — |
| 02 | [Scaffold do backend](02-backend-scaffold.md) | backend, infra | P | 01 |
| 03 | [Ambiente Docker](03-docker-dev-env.md) | infra | M | 02 |
| 04 | [CI + proteção da main](04-ci-pipeline.md) | infra | P | 02 |
| 05 | [`Node` + `LinkedList`](05-linked-list.md) | estrutura-de-dados | M | 02 |
| 06 | [`HashTable`](06-hash-table.md) | estrutura-de-dados | G | 05 |
| 07 | [`HashSet`](07-hash-set.md) | estrutura-de-dados | P | 06 |
| 08 | [`Product` + vocabulário](08-product-and-vocabulary.md) | backend | P | 02 |
| 09 | [Normalização de texto](09-text-normalizer.md) | backend | P | 07 |
| 10 | [`CatalogIndex`](10-catalog-index.md) | estrutura-de-dados, backend | M | 07, 08, 09 |
| 11 | [`ProductRepository`](11-product-repository.md) | backend | M | 03, 08 |
| 12 | [`GeminiTagGenerator`](12-gemini-tag-generator.md) | ia, backend | M | 08, 09 |
| 13 | [`CatalogService`](13-catalog-service.md) | backend | M | 10, 11, 12 |
| 14 | [Wiring da API](14-api-wiring.md) | backend | M | 13 |
| 15 | [Rotas de produtos e tags](15-api-products-tags.md) | backend | M | 14 |
| 16 | [Front: base + API + status](16-frontend-shell.md) | frontend | M | 03 |
| 17 | [Front: cadastro + lista](17-frontend-form-and-list.md) | frontend | M | 15, 16 |
| 18 | [Front: busca + filtros](18-frontend-search-and-filters.md) | frontend | M | 17 |
| 19 | [Front: admin + exclusão](19-frontend-admin-delete.md) | frontend | P | 17 |
| 20 | [Provisionar Supabase + Gemini](20-provision-cloud-accounts.md) | infra, manual | P | 03 |
| 21 | [Deploy via CI: Render + Netlify](21-deploy-render-netlify.md) | infra | M | 04, 15, 19, 20 |
| 22 | [Keep-alive + smoke test](22-keepalive-and-smoke-test.md) | infra | P | 21 |
| 23 | [README final](23-readme.md) | docs | M | 21 |
| 24 | [Release v1.0.0 e entrega](24-release-and-delivery.md) | docs, manual | P | 22, 23 |

## Grafo de dependências

```
01 ─▶ 02 ─┬─▶ 03 ─┬─▶ 11 ───────────────┐
          │       ├─▶ 16 ───────────┐   │
          │       └─▶ 20 (manual) ──┼───┼──────────────┐
          ├─▶ 04                    │   │              │
          ├─▶ 05 ─▶ 06 ─▶ 07 ─┬─▶ 09 ┼─┬─▶ 12 ─┐       │
          │                   │      │ │       │       │
          └─▶ 08 ─────────────┴──────┼─┴─▶ 10 ─┼─▶ 13 ─▶ 14 ─▶ 15 ─┐
                                     │         │                   │
                                     └─────────┴──── 17 ◀──────────┘
                                                     ├─▶ 18
                                                     └─▶ 19 ─▶ 21 ─┬─▶ 22 ─┐
                                                                   └─▶ 23 ─┴─▶ 24
```

## Ordem sugerida para hoje (21/11)

| Bloco | Cards | Observação |
|---|---|---|
| 1. Fundação | 01 → 02 → 03, 04 | 03 e 04 em paralelo |
| 2. Estruturas (TDD) | 05 → 06 → 07 | núcleo da nota; não apressar |
| 3. Domínio | 08, 09 → 10 | 08 pode começar junto com o bloco 2 |
| 4. Integrações | 11, 12 | independentes entre si; 20 (manual) pode ser feito aqui |
| 5. API | 13 → 14 → 15 | |
| 6. Front | 16 (já após 03) → 17 → 18, 19 | |
| 7. Produção | 21 → 22, 23 | |
| Até 04/12 | 24 | entrega |
