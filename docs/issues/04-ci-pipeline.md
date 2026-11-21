# 04 · CI no GitHub Actions + proteção da main

| Campo | Valor |
|---|---|
| Labels | `infra` |
| Tamanho | P |
| Depende de | 02 |
| Branch | `chore/04-ci-pipeline` |

## Objetivo
Lint + testes automáticos em todo push/PR; `main` protegida.

## Escopo
- [ ] `.github/workflows/ci.yml` (SPEC §16.2): `setup-uv` com versão fixada, `uv sync --frozen`, `ruff check`, `ruff format --check`, `pytest`
- [ ] `PYTHONHASHSEED=0` no job
- [ ] Badge do CI no `README.md`
- [ ] Branch protection na `main`: PR obrigatório + check do CI obrigatório

## Critérios de aceite
- [ ] PR de teste mostra o check verde
- [ ] Push direto na `main` é bloqueado

## Referências
SPEC §16.2, §18.3
