# Catálogo de Produtos com Tags Automáticas

[![CI](https://github.com/gabriel-barata/tfinal-produtos-com-tags-automaticas/actions/workflows/ci.yml/badge.svg)](https://github.com/gabriel-barata/tfinal-produtos-com-tags-automaticas/actions/workflows/ci.yml)

| | |
|---|---|
| **Site (Netlify)** | <https://catalogo-esportivo-p4.netlify.app> |
| **API (Render)** | <https://catalogo-esportivo-api.onrender.com> (health check: [`/health`](https://catalogo-esportivo-api.onrender.com/health)) |
| **Especificação** | [`docs/SPEC.md`](docs/SPEC.md) |

> A API roda no plano gratuito do Render, que hiberna após ~15 min sem tráfego. A primeira
> requisição pode levar cerca de 1 minuto; o site mostra um aviso enquanto a API acorda.

## O que o projeto faz

Projeto 4 de Estrutura de Dados I (IFG). É o catálogo de uma loja de artigos esportivos:

1. Você cadastra um produto (nome + descrição) e a IA (**Google Gemini**) gera as tags dele
   (departamento, esporte, público, cor e algumas tags livres).
2. O produto é salvo no Postgres (Supabase) e indexado em uma **tabela hash implementada do zero**.
3. A busca por texto livre ("tênis azul") é respondida **só pela tabela hash em memória**, com
   resultado ranqueado pelo número de termos que casaram.

O foco do trabalho são as estruturas de dados (`LinkedList`, `HashTable`, `HashSet`) escritas
sem usar `dict`, `set` ou `list` como armazenamento. Veja [Estruturas de dados](#estruturas-de-dados).

## Arquitetura

```
┌──────────────────┐   HTTPS/JSON   ┌──────────────────────────────────────────────┐
│  Frontend        │ ─────────────▶ │  Backend FastAPI (Render, Docker, 1 worker)  │
│  (Netlify)       │                │                                              │
│  HTML + ES mod.  │                │  routes ──▶ CatalogService                   │
│  + Pico.css      │                │               │        │         │           │
└──────────────────┘                │               ▼        ▼         ▼           │
                                    │     GeminiTagGenerator  CatalogIndex  ProductRepository
                                    │          │            (memória)          │   │
                                    │          │       ┌───────────────┐       │   │
                                    │          │       │ HashTable     │       │   │
                                    │          │       │ id → Product  │       │   │
                                    │          │       │ HashTable     │       │   │
                                    │          │       │ tag → HashSet │       │   │
                                    │          │       └───────────────┘       │   │
                                    └──────────┼───────────────────────────────┼───┘
                                               ▼                               ▼
                                    ┌────────────────────┐        ┌──────────────────────┐
                                    │ Google Gemini API  │        │ Supabase (Postgres)  │
                                    │ (free tier)        │        │ tabela `products`    │
                                    └────────────────────┘        └──────────────────────┘
```

| Componente | Papel |
|---|---|
| `CatalogIndex` (tabelas hash) | **Motor de busca e leitura.** Toda consulta é respondida a partir dele; não faz I/O |
| Supabase (Postgres) | **Persistência durável.** Só recebe `INSERT`, `DELETE` e um `SELECT *` no startup para reconstruir o índice. Nenhuma busca vira SQL |
| Gemini | Gera as tags **no cadastro**. Nunca é chamado em buscas |

**Cadastro:** Gemini gera as tags → normalização → `INSERT` → `CatalogIndex.add`. Se a IA falhar
(após 1 nova tentativa), a API responde `503` e nada é salvo. Se o banco falhar, responde `500` e
nada é indexado.

**Busca:** `tokenize_query` → para cada termo, lookup no índice invertido (`tag → ids`) → placar
(também uma `HashTable`) → ordenação final. **Zero SQL.**

**Startup:** a API lê todos os produtos do banco e reconstrói o índice. Se o banco estiver
inacessível, o processo encerra (fail fast).

## Estruturas de dados

Ficam em [`backend/app/data_structures/`](backend/app/data_structures/) e não importam nada do
restante da aplicação.

### Como funciona uma hash table

1. Um **array de buckets** de tamanho fixo (ex.: 8).
2. A chave vira índice: `hash(chave) % capacidade`.
3. **Colisão** acontece quando duas chaves caem no mesmo bucket. Com **encadeamento separado**,
   cada bucket é uma lista encadeada de pares `(chave, valor)`.
4. Buscar = calcular o bucket + percorrer só aquela cadeia (normalmente 0–2 nós).
5. **Resize**: quando `itens / capacidade > 0,75`, cria um array com o **dobro** da capacidade e
   reinsere tudo, porque o `% capacidade` mudou.
6. **HashSet** = hash table que só guarda chaves.

```
capacidade = 4
[0] → ∅
[1] → ("calcado", …) → ∅
[2] → ∅
[3] → ("azul", …) → ("corrida", …) → ∅      ← colisão resolvida por encadeamento
```

### Decisões de implementação

| Item | Decisão |
|---|---|
| Array base | `[None] * capacity`; buckets criados sob demanda (`None` até a 1ª inserção) |
| Colisão | encadeamento separado com `LinkedList` própria |
| Função hash | `hash()` builtin |
| Índice do bucket | `hash(key) % capacity` (em Python o resultado é sempre ≥ 0) |
| Capacidade inicial | 8 (parâmetro `initial_capacity`, mínimo 1) |
| Fator de carga máximo | 0,75 (constante `MAX_LOAD_FACTOR`) |
| Resize | dobra a capacidade e reinsere todos os pares (rehash) |
| Shrink | não implementado |
| Inserção na cadeia | no início da lista (O(1)); se a chave já existe, atualiza o valor |
| Interface | estilo `dict` (`[]`, `in`, `len`, `del`, iteração) + métodos nomeados |
| Thread-safety | **não** (como `dict`); a sincronização fica no `CatalogIndex` |

Chaves `int` têm `hash(n) == n`, então ids sequenciais se distribuem uniformemente entre os buckets.

**Regra de Ouro:** em `data_structures/` e em `services/catalog_index.py` não há `dict`, `set`,
`list` nem `collections.*` guardando produtos, o índice de tags ou o placar da busca. Os arrays
são `[None] * n` e as sequências imutáveis são `tuple`. Usar `dict`/`set` nos **testes** como
oráculo de comparação é permitido.

### Complexidade

`n` = itens na tabela, `t` = tags do produto, `q` = termos da busca, `m` = soma dos ids
encontrados nas tags da busca, `r` = resultados, `N` = produtos no banco. O pior caso de
`O(n)` ocorre quando todas as chaves colidem no mesmo bucket.

| Operação | Média | Pior caso |
|---|---|---|
| `HashTable.put` | O(1) amortizado | O(n) |
| `HashTable.get` / `contains` / `remove` | O(1) | O(n) |
| `HashTable._resize` | O(n) | O(n) |
| Iteração | O(n + capacidade) | O(n + capacidade) |
| `CatalogIndex.add` / `remove` | O(t) | O(t·n) |
| `CatalogIndex.search` | O(q + m + r log r) | — |
| Rebuild no startup | O(N·t) | — |

Cada método público das estruturas tem docstring em pt-BR com complexidade média e pior caso e
as exceções lançadas.

## Por que Gemini e não Ollama

O kit de ferramentas da disciplina cita o **Ollama** (modelos locais como phi3/llama3). Este
projeto usa o **Google Gemini (free tier)** por três motivos:

- o Ollama não roda no plano gratuito do Render (512 MB de RAM, 0,1 CPU; modelos leves exigem
  ~2–4 GB);
- os guias de laboratório do professor (Supabase/Render) já usam Gemini;
- custo zero é requisito do projeto.

A saída do Gemini é estruturada (`response_schema` com `enum` nos grupos fechados), e as tags
passam por normalização antes de entrar no índice. Não há fallback por palavras-chave: se a IA
falhar, o cadastro falha com `503`.

## Como rodar localmente

**Pré-requisitos:** Docker com Compose, `make` e uma chave do Gemini
([Google AI Studio](https://aistudio.google.com/apikey)). O Gemini é real mesmo em dev.

```bash
cp .env.example .env     # preencha GEMINI_API_KEY
make up                  # sobe api, banco e site
```

| Serviço | URL |
|---|---|
| Site | <http://localhost:8080> |
| API | <http://localhost:8000> (docs interativas em `/docs`) |
| Postgres | `localhost:5432` |

Na primeira subida o banco aplica `supabase/migrations/001_create_products.sql`. A chave de
administrador (exclusão de produtos) em dev é `dev-admin-key`; no site, use o painel de admin.

| Comando | O que faz |
|---|---|
| `make up` / `make down` | sobe / derruba o ambiente |
| `make logs` | segue os logs da API |
| `make test` | roda o `pytest` no container |
| `make lint` / `make format` | `ruff check` + `ruff format --check` / `ruff format` |
| `make reset-db` | apaga o volume do banco; a migração é reaplicada no próximo `make up` |

**Teste ponta a ponta** (cadastra, busca e exclui um produto; usa só a biblioteca padrão):

```bash
python scripts/smoke_test.py http://localhost:8000 --admin-key dev-admin-key
```

## Como fazer deploy

O **único** caminho até a produção é o workflow [`ci.yml`](.github/workflows/ci.yml). Render e
Netlify não observam o repositório; só executam o que o pipeline entrega.

```
push na main:   lint + testes ──▶ deploy-api ──▶ deploy-web
PR / branches:  lint + testes
```

- **`deploy-api`**: build da imagem Docker (`target: prod`), push para o GHCR (`:<sha>` e
  `:latest`), chamada ao deploy hook do Render e espera do `/health`.
- **`deploy-web`**: publica `frontend/` no Netlify via CLI, só depois de a API responder.
- O workflow [`keep-alive.yml`](.github/workflows/keep-alive.yml) chama `/health` a cada 3 dias
  para o Supabase gratuito não pausar por inatividade.

**Primeiro deploy** (uma vez):

1. **Supabase:** criar o projeto, rodar `supabase/migrations/001_create_products.sql` e copiar a
   URL do *Session pooler* (porta 5432).
2. **Gemini:** criar a chave no Google AI Studio.
3. **Netlify:** gerar um token pessoal, criar um site vazio e **sem vínculo com Git** pela API
   (`POST /api/v1/sites`) e anotar o Project ID.
4. **GHCR:** depois do primeiro push da imagem, tornar o pacote **público** (o Render puxa sem
   credencial).
5. **Render:** criar um Blueprint a partir do repositório (`render.yaml`), preencher os secrets e
   copiar o deploy hook.
6. **GitHub** (ambiente `production`): secrets `RENDER_DEPLOY_HOOK_URL`, `NETLIFY_AUTH_TOKEN` e
   `NETLIFY_SITE_ID`; variable `BACKEND_URL`.
7. Apontar `API_BASE_URL` em `frontend/js/config.js` para a URL do Render.
8. Rodar `scripts/smoke_test.py` contra a URL de produção.

Depois disso, todo push na `main` com CI verde publica API e site sem passo manual.

## Variáveis de ambiente

**Aplicação** (`.env` em dev, painel do Render em produção):

| Variável | Exemplo | Descrição |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres.<ref>:<senha>@aws-0-<região>.pooler.supabase.com:5432/postgres` | Conexão com o Postgres. Em dev é definida pelo `docker-compose` |
| `GEMINI_API_KEY` | `AIza…` | Chave do Gemini (secret) |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Modelo Flash/Flash-Lite do free tier |
| `ADMIN_KEY` | `dev-admin-key` | Chave do header `X-Admin-Key` para excluir produtos. Se vazia, a exclusão sempre responde `401` |
| `ALLOWED_ORIGINS` | `https://catalogo-esportivo-p4.netlify.app` | Origens CORS, separadas por vírgula |
| `LOG_LEVEL` | `INFO` | Nível de log |

**Pipeline** (GitHub, ambiente `production`):

| Nome | Tipo | Uso |
|---|---|---|
| `RENDER_DEPLOY_HOOK_URL` | secret | dispara o deploy da imagem no Render |
| `NETLIFY_AUTH_TOKEN` | secret | token pessoal do Netlify |
| `NETLIFY_SITE_ID` | secret | site do front |
| `BACKEND_URL` | variable | URL da API (espera do `/health` e keep-alive) |

As credenciais do banco e do Gemini ficam só no Render; não passam pelo GitHub.

## Estrutura de pastas

```
.
├── backend/
│   ├── Dockerfile               # stages base / dev / prod (mesmo arquivo em dev e produção)
│   ├── pyproject.toml           # dependências (uv) e config do ruff
│   ├── app/
│   │   ├── main.py              # app FastAPI, CORS, lifespan, handlers de exceção
│   │   ├── config.py            # Settings (variáveis de ambiente)
│   │   ├── dependencies.py      # providers de Depends + verificação do X-Admin-Key
│   │   ├── exceptions.py
│   │   ├── data_structures/     # LinkedList, HashTable, HashSet (do zero)
│   │   ├── models/              # Product, vocabulário base de tags
│   │   ├── schemas/             # contratos HTTP (Pydantic)
│   │   ├── routes/              # endpoints, só HTTP
│   │   ├── services/            # CatalogIndex, CatalogService, GeminiTagGenerator
│   │   ├── repositories/        # ProductRepository (SQL)
│   │   └── utils/               # normalização de texto
│   └── tests/                   # espelha app/
├── frontend/                    # HTML + ES modules + Pico.css, sem build
├── supabase/migrations/         # 001_create_products.sql
├── scripts/smoke_test.py        # teste ponta a ponta contra uma URL
├── .github/workflows/           # ci.yml (testes + deploy) e keep-alive.yml
├── docs/                        # SPEC.md e cards (docs/issues)
├── docker-compose.yml           # api, db e web para desenvolvimento
├── render.yaml                  # Blueprint do Render (imagem do GHCR)
├── netlify.toml                 # publica frontend/ sem build
└── Makefile
```

## Documentação

A especificação completa (decisões, contratos da API, fluxos e critérios de aceite) está em
[`docs/SPEC.md`](docs/SPEC.md).
