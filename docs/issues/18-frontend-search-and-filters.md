# 18 · Frontend: busca e filtros por tag

| Campo | Valor |
|---|---|
| Labels | `frontend` |
| Tamanho | M |
| Depende de | 17 |
| Branch | `feat/18-frontend-search-and-filters` |

## Objetivo
Busca por texto com debounce e chips de filtro das tags base.

## Escopo
- [ ] `js/components/search-bar.js`: input com debounce de 300 ms → `listProducts(q)` → `product-list.render`; expõe `addTerm`/`removeTerm`
- [ ] `js/components/tag-filters.js`: carrega `/api/tags`, agrupa em Departamento/Esporte/Público/Cor (ignora `free`), chip com contagem; clique alterna o termo na busca; estado ativo visual
- [ ] Recarregar os filtros após cadastro/exclusão

## Critérios de aceite
- [ ] Digitar "tênis azul" destaca `tenis` e `azul` nos cards e ordena por score
- [ ] Clicar em `corrida` adiciona o termo; clicar de novo remove
- [ ] Contagens dos chips batem com `/api/tags`

## Referências
SPEC §12.5, CA2–CA6, CA12
