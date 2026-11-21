# 02 · Scaffold do backend (uv, FastAPI, ruff, pytest)

| Campo | Valor |
|---|---|
| Labels | `backend`, `infra` |
| Tamanho | P |
| Depende de | 01 |
| Branch | `chore/02-backend-scaffold` |

## Objetivo
Esqueleto do projeto Python com tooling configurado e a árvore de pastas da SPEC criada.

## Escopo
- [ ] `backend/.python-version` = 3.12
- [ ] `backend/pyproject.toml` (uv): runtime `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `google-genai`, `psycopg[binary,pool]`; dev `pytest`, `httpx`, `ruff`
- [ ] `uv.lock` gerado e versionado
- [ ] Config do ruff: linha 100, regras `E,F,I,B,UP,N,SIM`
- [ ] Config do pytest: `testpaths = ["tests"]`
- [ ] Árvore `app/{data_structures,models,schemas,routes,services,repositories,utils}` com `__init__.py`
- [ ] `app/config.py` com `Settings` (campos da SPEC §11.4)
- [ ] `app/main.py` mínimo com `GET /health` retornando `{"status": "ok"}` (stub)
- [ ] `tests/` espelhando `app/` + `conftest.py` vazio + 1 teste do `/health`

## Critérios de aceite
- [ ] `uv sync && uv run pytest` passa
- [ ] `uv run ruff check . && uv run ruff format --check .` passa
- [ ] `uv run uvicorn app.main:app` sobe e `/health` responde

## Referências
SPEC §11.1, §11.4, §11.5
