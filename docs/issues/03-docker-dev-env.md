# 03 · Ambiente de desenvolvimento com Docker

| Campo | Valor |
|---|---|
| Labels | `infra` |
| Tamanho | M |
| Depende de | 02 |
| Branch | `chore/03-docker-dev-env` |

## Objetivo
`make up` sobe API + Postgres local + nginx servindo o front, com a migração aplicada automaticamente.

## Escopo
- [ ] `backend/Dockerfile` multi-stage: `base` → `dev` → `prod` (último). `uv` via imagem oficial com versão fixada. `prod`: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1`
- [ ] `backend/.dockerignore`
- [ ] `supabase/migrations/001_create_products.sql` (SPEC §10.1, com RLS ligado)
- [ ] `docker-compose.yml`: serviços `api` (target `dev`, reload, volumes `app/` e `tests/`), `db` (`postgres:16-alpine`, healthcheck, migração em `/docker-entrypoint-initdb.d`), `web` (`nginx:alpine`, porta 8080)
- [ ] `frontend/index.html` placeholder (só para o nginx servir algo)
- [ ] `.env.example` na raiz (SPEC §15.4)
- [ ] `Makefile`: `up`, `down`, `logs`, `test`, `lint`, `format`, `reset-db`

## Critérios de aceite
- [ ] `cp .env.example .env && make up` → `localhost:8000/health` ok e `localhost:8080` serve o placeholder
- [ ] Tabela `products` existe no Postgres do container
- [ ] `make test` e `make lint` rodam dentro do container
- [ ] `docker build backend/` (stage padrão) gera a imagem de produção

## Referências
SPEC §10.1, §15
