# 22 · Keep-alive agendado + smoke test

| Campo | Valor |
|---|---|
| Labels | `infra` |
| Tamanho | P |
| Depende de | 21 |
| Branch | `chore/22-keepalive-smoke` |

## Objetivo
Evitar a pausa do Supabase free e ter uma verificação ponta a ponta reproduzível.

## Escopo
- [ ] `.github/workflows/keep-alive.yml`: cron `0 12 */3 * *` + `workflow_dispatch`; `curl --fail --retry 5 --max-time 90 "$BACKEND_URL/health"`
- [ ] Repository variable `BACKEND_URL`
- [ ] `scripts/smoke_test.py` (stdlib apenas): recebe URL base e chave admin por argumento/env; cadastra um produto, busca por uma tag dele, confere `/api/tags`, exclui, confere que sumiu

## Critérios de aceite
- [ ] Execução manual do workflow fica verde
- [ ] `smoke_test.py` passa contra local e contra produção

## Referências
SPEC §16.1, §17.5
