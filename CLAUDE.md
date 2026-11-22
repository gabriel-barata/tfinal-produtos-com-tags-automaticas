# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Pre-implementation. The repo currently holds only `docs/SPEC.md` (approved spec, decisions D01–D25) and `docs/issues/NN-slug.md` (24 cards, mirrored in Trello; dependency graph in `docs/issues/README.md`). No code, no commits yet. **The spec is the source of truth: do not add scope, files, rules or test-coverage targets that it doesn't contain; if something seems missing, ask first.** Commands below are the *planned* ones from the spec (§15–16) and only work once cards 01–04 are done.

## What it is

University project (EDD1, IFG, "Projeto 4"): sports-store catalog where Gemini generates tags for a product and the product is indexed in a **hand-written hash table** for tag search. Delivery 2026-12-04 (GitHub repo link + README).

Grading: 70% data structures built from scratch, 20% AI integration feeding the structure, 10% readable/commented code.

## Commands (planned)

```bash
cp .env.example .env     # needs GEMINI_API_KEY (real Gemini even in dev)
make up                  # docker compose: api :8000, db (postgres:16), web (nginx) :8080
make test                # docker compose run --rm api pytest
make lint                # ruff check . && ruff format --check .
make format
make reset-db            # down -v; migration reapplied on next up
# single test, from backend/ (or via docker compose run --rm api):
PYTHONHASHSEED=0 uv run pytest tests/data_structures/test_hash_table.py::test_name
```

Backend: Python 3.12, `uv`, FastAPI, psycopg 3 (raw SQL), ruff (line 100, rules `E,F,I,B,UP,N,SIM`). Frontend: vanilla JS ES modules + Pico.css, no build.

## Architecture (big picture)

- **In-memory `CatalogIndex` answers every read/search**; Postgres (Supabase) is durable storage only (`INSERT`, `DELETE`, one `SELECT *` at startup to rebuild the index). Never put search logic in SQL. Gemini is called only on product creation, never on search.
- Index = `HashTable[int, Product]` + inverted index `HashTable[str, HashSet[int]]` (tag → product ids). Removing a product drops tags whose set becomes empty. Search is ranked OR: score = number of matched terms, ties → higher id first; the score accumulator is also a `HashTable`.
- Layers in `backend/app/` (one class per file, **no subfolders inside layers**): `data_structures/` (generic, imports nothing from the app) · `models/` · `schemas/` (Pydantic, HTTP contracts) · `routes/` (HTTP only, talks to `CatalogService`) · `services/` (`catalog_index`, `catalog_service`, `tag_generator`) · `repositories/` · `utils/text_normalizer`. `CatalogIndex` does no I/O. `CatalogService` is the only one that knows generator + repository + index; the latter two are injected (tests use fakes).
- Create flow: Gemini tags → normalize → `INSERT` → `index.add`. AI failure (after 1 retry) → 503, nothing saved; DB failure → 500, nothing indexed. Delete: check index → `DELETE` → `index.remove`, guarded by `X-Admin-Key`.
- Tags: closed groups (`department`, `sports`, `audience`, `colors`, enforced via Gemini `response_schema` enum, schema generated from `BASE_VOCABULARY`) + 1–4 free one-word tags. Every AI tag goes through `normalize_tag(s)` (lowercase, strip accents, `[a-z0-9]` only, split compounds, drop stopwords); queries go through `tokenize_query`. Sport "tênis" is `raquete`; `tenis` is the shoe.
- **Concurrency: exactly 1 uvicorn worker** (each process would have its own index); `threading.RLock` lives inside `CatalogIndex`, not in `data_structures/`; the Gemini call happens outside the lock. Startup fails fast if the DB is unreachable.
- Deploy (D26): **only via `ci.yml`** on push to `main` (lint/tests → `deploy-api` → `deploy-web`). CI builds Dockerfile `--target prod`, pushes to GHCR (`:<sha>`), calls the Render deploy hook (`render.yaml`, `runtime: image`, `autoDeploy: false`); Netlify via CLI (`frontend/`, site not linked to Git). Render/Netlify never watch the repo. Supabase Session pooler (IPv4, port 5432; not the transaction pooler). Migration `supabase/migrations/001_create_products.sql` (RLS on, no policies) is shared by dev (docker-entrypoint-initdb) and prod (manual).
- Frontend: only `js/api.js` does `fetch`; components export `mount(element, options)` and talk through callbacks wired in `main.js`.

## Hard rules

- **"Regra de Ouro"**: no `dict`, `set`, `list` or `collections.*` as storage for products, the tag index or the search score board (`data_structures/` and `services/catalog_index.py`). No `list.append` inside the structures; use `[None] * n` arrays and `tuple`. Built-ins like `hash()`, `sorted()`, `len()` and `dict`/`list` for JSON payloads, schemas, config are fine. `dict`/`set` are used only as **test oracles**.
- HashTable: separate chaining with own `LinkedList`, builtin `hash()`, initial capacity 8, resize ×2 when load > 0.75, no shrink, dict-like interface. Develop `data_structures/` test-first (oracle with 10 000 seeded random ops + a `CollidingKey` with constant `__hash__`). No test may depend on a specific `hash()` value.
- Public methods of the structures need pt-BR docstrings with average/worst-case Big-O and raised exceptions.
- Language: identifiers, commits, logs in English; comments, docstrings, README, `docs/`, API errors, UI text in pt-BR; tags in pt-BR without accents. Comments explain *why*.
- No Ollama (Gemini free tier, decision D02), no keyword fallback when AI fails, no extras (benchmarks, HashTable visualizer, seeds, demo video).
- Git: public repo; no direct push to `main`; one branch per Trello card (`feat|fix|chore|docs|test/<NN>-slug`), PR + CI green + squash merge; Conventional Commits; tag `v1.0.0` on delivery.
- Merges are always done by the user, never by Claude: open the PR, wait for CI, then stop. Never run `gh pr merge`.
- Trello: when working a card, move it on the Trello board as its state changes (start → in progress, PR open/merged → matching list). Don't leave it for the user.
