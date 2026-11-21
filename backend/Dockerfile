# Stages: base -> dev -> prod. O prod fica por último porque é o alvo padrão
# (o Render constrói o último stage), então dev e produção partem do mesmo arquivo.

# Versão do uv fixada para builds reproduzíveis.
FROM ghcr.io/astral-sh/uv:0.12.22 AS uv

FROM python:3.12-slim AS base
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
# copy: o cache do uv fica em outro filesystem que o .venv e hardlinks falhariam.
ENV UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
# Copiar só os manifestos primeiro mantém a camada de dependências em cache.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

FROM base AS dev
RUN uv sync --frozen
# app/ e tests/ entram por volume no compose; --reload recarrega ao editar.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS prod
COPY app ./app
# Exatamente 1 worker: o índice vive em memória, cada processo teria o seu.
# Forma shell + exec para expandir ${PORT} (injetada pelo Render).
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
