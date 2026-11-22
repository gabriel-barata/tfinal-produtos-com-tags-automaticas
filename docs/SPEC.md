# Especificação — Catálogo de Produtos com Tags Automáticas (MVP)

> Projeto 4 · Estrutura de Dados I · Bacharelado em Sistemas de Informação (IFG)
> Versão 1.0 · 21/11/2026 · Status: **aguardando revisão**

---

## Sumário

1. [Contexto](#1-contexto)
2. [Restrições da avaliação](#2-restrições-da-avaliação)
3. [Escopo do MVP](#3-escopo-do-mvp)
4. [Arquitetura](#4-arquitetura)
5. [Estruturas de dados](#5-estruturas-de-dados)
6. [Domínio: produto e vocabulário de tags](#6-domínio-produto-e-vocabulário-de-tags)
7. [Geração de tags com IA (Gemini)](#7-geração-de-tags-com-ia-gemini)
8. [Índice em memória e busca](#8-índice-em-memória-e-busca)
9. [API HTTP](#9-api-http)
10. [Persistência (Supabase / Postgres)](#10-persistência-supabase--postgres)
11. [Backend: estrutura e responsabilidades](#11-backend-estrutura-e-responsabilidades)
12. [Frontend](#12-frontend)
13. [Concorrência e consistência](#13-concorrência-e-consistência)
14. [Segurança](#14-segurança)
15. [Ambiente de desenvolvimento (Docker)](#15-ambiente-de-desenvolvimento-docker)
16. [Testes e CI](#16-testes-e-ci)
17. [Deploy e produção](#17-deploy-e-produção)
18. [Convenções de código, idioma e Git](#18-convenções-de-código-idioma-e-git)
19. [Documentação entregue (README)](#19-documentação-entregue-readme)
20. [Critérios de aceite do MVP](#20-critérios-de-aceite-do-mvp)
21. [Riscos e mitigações](#21-riscos-e-mitigações)
22. [Marcos](#22-marcos)
23. [Registro de decisões](#23-registro-de-decisões)
24. [Fora de escopo / pós-MVP](#24-fora-de-escopo--pós-mvp)

---

## 1. Contexto

### 1.1 Enunciado (Projeto 4)

> **O problema:** um e-commerce precisa categorizar produtos novos rapidamente para que os clientes os encontrem na busca.
>
> 1. Receber o nome e a descrição de um produto, como: "Tênis azul para corrida em asfalto".
> 2. Pedir à IA que analise a descrição e gere tags relevantes (ex.: "calçado", "esporte", "corrida", "azul").
> 3. Armazenar o produto em uma Tabela de Dispersão (Hash Table), usando as tags para ajudar a organizar e permitir buscas rápidas.
> 4. Implementar uma função de busca que use essas tags para encontrar os produtos.
>
> **Estrutura de dados principal:** Tabela de Dispersão (Hash Table) ou Dicionários.

### 1.2 Cenário de negócio adotado

Como o enunciado não define regra de negócio, o MVP simula uma **loja de artigos esportivos**. Um domínio fechado deixa o vocabulário de tags controlável e a validação manual simples.

Nome provisório da aplicação: **Catálogo Esportivo**. Pode ser trocado sem impacto técnico.

### 1.3 Material de referência do professor

| Material | Conteúdo | Uso neste projeto |
|---|---|---|
| `Projetos.pdf` | enunciados P1–P4, kit de ferramentas, "Regra de Ouro", rubrica | **fonte das restrições** |
| `Guia_Passo_a_Passo…pdf` | GitHub + Antigravity + Netlify | só a parte de Netlify |
| `Supabase.pdf` | criação de banco, pooler IPv4, chave Gemini | referência de setup |
| `Render.pdf` | deploy FastAPI no Render | referência de setup |
| repo `profMattiazzo/projeto1` | implementação do P1 (helpdesk) | **não reaproveitado** (ver §23, D01) |

---

## 2. Restrições da avaliação

### 2.1 Rubrica

| Peso | Critério | Como o projeto atende |
|---|---|---|
| **70%** | Estrutura de dados construída corretamente, **sem bibliotecas prontas**; operações funcionando | `HashTable`, `HashSet` e `LinkedList` próprias (§5), testadas com `dict` como oráculo |
| **20%** | Integração com IA alimentando a estrutura | Gemini gera as tags, que são indexadas na `HashTable` (§7, §8) |
| **10%** | Código legível, comentado, bem estruturado | camadas (§11), docstrings pt-BR com Big-O, ruff, CI |

**Entrega:** link do repositório GitHub + `README.md` explicando como rodar. Vídeo é opcional e **não** será feito (ver D16).

### 2.2 "Regra de Ouro": construir do zero

Texto do professor: *"Vocês NÃO PODEM usar as implementações prontas de estruturas de dados do Python. Proibido: `list.append()`, `queue.Queue`, `collections.deque` etc. para a estrutura principal do projeto."*

**Política de uso de built-ins adotada** (vale para todo o código):

| Permitido | Proibido |
|---|---|
| `hash()`, `sorted()`, `len()`, `isinstance()`, funções de `str` | `dict`, `set`, `list`, `collections.*` como **armazenamento** de produtos, do índice de tags ou do placar da busca |
| `[None] * n` como array de tamanho fixo (nunca `append`) | `list.append` dentro das estruturas |
| `tuple` para coleções imutáveis pequenas (tags de um produto) | |
| `dict`/`list` em código que **não é** a estrutura principal: payload JSON, schemas Pydantic, config, kwargs, resposta HTTP serializada | |
| `dict` como **oráculo** nos testes | |

### 2.3 Divergência consciente: Gemini em vez de Ollama

O kit de ferramentas do professor cita **Ollama** (phi3/llama3 local), e a rubrica dos 20% menciona "comunicar com o Ollama". Este projeto usa **Google Gemini (free tier)** porque:

- Ollama não roda no plano gratuito do Render (512 MB de RAM, 0,1 CPU; modelos leves exigem ~2–4 GB);
- os próprios guias de laboratório do professor (Supabase/Render) usam Gemini;
- custo zero é requisito do projeto.

A justificativa fica registrada no README (§19) para o avaliador.

---

## 3. Escopo do MVP

### 3.1 Dentro do escopo

| # | Funcionalidade |
|---|---|
| F1 | Cadastrar produto (nome + descrição): a IA gera as tags, o produto é salvo e indexado |
| F2 | Buscar produtos por texto livre, com OR ranqueado sobre as tags |
| F3 | Listar todos os produtos (busca vazia), mais recentes primeiro |
| F4 | Obter um produto por id |
| F5 | Listar tags com contagem e grupo (alimenta os filtros do front) |
| F6 | Excluir produto (exige chave de administrador) |
| F7 | Reconstrução do índice em memória a partir do banco no startup |
| F8 | Frontend web de página única com cadastro, busca, filtros e exclusão |
| F9 | Ambiente de desenvolvimento em Docker Compose |
| F10 | Deploy gratuito: Render (API), Netlify (front), Supabase (banco) |
| F11 | CI/CD único no GitHub Actions: lint, testes e deploy; keep-alive agendado |
| F12 | Documentação de complexidade (Big-O) nas estruturas e no README |

### 3.2 Fora do escopo

Ver §24.

---

## 4. Arquitetura

### 4.1 Visão geral

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

### 4.2 Papéis

| Componente | Papel | Nunca faz |
|---|---|---|
| `CatalogIndex` (HashTables) | **motor de busca e leitura**: toda consulta é respondida a partir dele | I/O (rede, banco) |
| Supabase | **persistência durável** ("HD"): só recebe `INSERT`, `DELETE` e um `SELECT *` no startup | responder buscas (nenhum `WHERE`/`ILIKE` de busca) |
| Gemini | gerar tags no cadastro | ser chamado em buscas |

### 4.3 Fluxos

**Cadastro (F1)**
1. Front envia `POST /api/products {name, description}`.
2. `CatalogService` pega as tags livres mais usadas no índice (até 100) e chama `GeminiTagGenerator`.
3. Gemini devolve JSON estruturado → validação → normalização → `tuple` de tags.
4. `ProductRepository.insert` → Postgres gera `id` e `created_at`.
5. `CatalogIndex.add(product)` → insere em `products` e adiciona o id no `HashSet` de cada tag.
6. Responde `201` com o produto.

Se a IA falhar (após 1 retry) → `503`, **nada é salvo**. Se o banco falhar → `500`, **nada é indexado**.

**Busca (F2/F3)**
1. Front envia `GET /api/products?q=tênis azul`.
2. `tokenize_query` → `("tenis", "azul")`.
3. `CatalogIndex.search` → lookup de cada termo no `tag_index`, placar numa `HashTable`, ordenação final.
4. Responde com lista de `{product, score, matched_tags}`. **Zero SQL.**

**Startup (F7)**
1. `lifespan` do FastAPI → `CatalogService.load_index()`.
2. `ProductRepository.load_all()` (`SELECT * ORDER BY id`) → `CatalogIndex.add` para cada produto.
3. Se o banco estiver inacessível → **fail fast** (processo encerra com log claro; o Render reinicia).

**Exclusão (F6)**
1. `DELETE /api/products/{id}` com header `X-Admin-Key`.
2. Valida a chave → verifica existência no índice → `DELETE` no banco → `CatalogIndex.remove`.
3. Ao remover, o id sai do `HashSet` de cada tag; **tags cujo set fica vazio são removidas do índice**.

---

## 5. Estruturas de dados

Local: `backend/app/data_structures/`. Pacote **genérico**: não importa nada do restante da aplicação.

### 5.1 Como funciona uma hash table (resumo didático, também vai no README)

1. Um **array de buckets** de tamanho fixo (ex.: 8).
2. A chave vira índice: `hash(chave) % capacidade`.
3. **Colisão** acontece quando duas chaves caem no mesmo bucket. Com **encadeamento separado**, cada bucket é uma lista encadeada de pares `(chave, valor)`.
4. Buscar = calcular o bucket + percorrer só aquela cadeia (normalmente 0–2 nós).
5. **Resize**: quando `itens / capacidade > 0,75`, cria um array com o **dobro** da capacidade e reinsere tudo, porque o `% capacidade` mudou.
6. **HashSet** = hash table que só guarda chaves.

```
capacidade = 4
[0] → ∅
[1] → ("calcado", …) → ∅
[2] → ∅
[3] → ("azul", …) → ("corrida", …) → ∅      ← colisão resolvida por encadeamento
```

### 5.2 Decisões de implementação

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
| Interface | estilo `dict` (dunders) + métodos nomeados |
| Thread-safety | **não** (como `dict`); sincronização fica no `CatalogIndex` (§13) |

Observação para o README: chaves `int` têm `hash(n) == n`, então ids sequenciais se distribuem uniformemente entre os buckets.

### 5.3 `Node` e `LinkedList` (`linked_list.py`)

Lista simplesmente encadeada de pares chave/valor, usada como bucket.

```python
class Node:
    """Nó da lista encadeada: guarda um par chave/valor e o ponteiro para o próximo."""
    key: object
    value: object
    next: "Node | None"

class LinkedList:
    head: Node | None
    _size: int

    def insert_front(self, key, value) -> None          # O(1)
    def find_node(self, key) -> Node | None             # O(k), k = tamanho da cadeia
    def remove(self, key) -> object                     # O(k); KeyError se ausente; devolve o valor
    def __iter__(self) -> Iterator[Node]                # O(k)
    def __len__(self) -> int                            # O(1)
    def __bool__ / __repr__
```

### 5.4 `HashTable` (`hash_table.py`)

```python
class HashTable(Generic[K, V]):
    MAX_LOAD_FACTOR = 0.75

    def __init__(self, initial_capacity: int = 8) -> None

    # Operações principais
    def put(self, key: K, value: V) -> None             # média O(1) amortizado; pior O(n)
    def get(self, key: K, default: V | None = None) -> V | None   # média O(1); pior O(n)
    def remove(self, key: K) -> V                       # média O(1); KeyError se ausente
    def contains(self, key: K) -> bool                  # média O(1)

    # Iteração
    def keys(self) -> Iterator[K]                       # O(n + capacidade)
    def values(self) -> Iterator[V]
    def items(self) -> Iterator[tuple[K, V]]

    # Interface estilo dict
    def __setitem__(self, key, value)                   # = put
    def __getitem__(self, key)                          # KeyError se ausente
    def __delitem__(self, key)                          # = remove
    def __contains__(self, key)                         # = contains
    def __len__(self) -> int                            # O(1)
    def __iter__(self)                                  # = keys()
    def __repr__(self) -> str

    # Introspecção
    @property
    def capacity(self) -> int
    @property
    def load_factor(self) -> float

    # Internos
    def _bucket_index(self, key: K) -> int
    def _resize(self, new_capacity: int) -> None        # O(n)
```

### 5.5 `HashSet` (`hash_set.py`)

Wrapper fino sobre `HashTable[K, None]`.

```python
class HashSet(Generic[K]):
    def add(self, item: K) -> None                      # média O(1)
    def remove(self, item: K) -> None                   # KeyError se ausente
    def discard(self, item: K) -> None                  # silencioso se ausente
    def __contains__(self, item: K) -> bool
    def __len__(self) -> int
    def __iter__(self) -> Iterator[K]
    def __repr__(self) -> str
```

### 5.6 Documentação de complexidade

Cada método público das três classes tem docstring em pt-BR com:
- descrição do comportamento;
- complexidade **média** e **pior caso**;
- exceções lançadas.

O README traz a tabela consolidada (§19).

---

## 6. Domínio: produto e vocabulário de tags

### 6.1 Entidade `Product` (`models/product.py`)

```python
@dataclass(frozen=True)
class Product:
    id: int
    name: str
    description: str
    tags: tuple[str, ...]
    created_at: datetime
```

| Campo | Regra |
|---|---|
| `id` | gerado pelo Postgres (`identity`) |
| `name` | obrigatório, 2–120 caracteres após `strip()` |
| `description` | obrigatório, 10–1000 caracteres após `strip()` |
| `tags` | geradas pela IA, normalizadas, sem duplicatas, não editáveis |
| `created_at` | gerado pelo banco (`timestamptz`) |

Não há unicidade de nome: dois produtos podem ter o mesmo nome.

### 6.2 Vocabulário base (`models/tag_vocabulary.py`)

```python
class TagGroup(StrEnum):
    DEPARTMENT = "department"
    SPORTS = "sports"
    AUDIENCE = "audience"
    COLORS = "colors"
    FREE = "free"
```

| Grupo | Quantidade por produto | Valores (31 no total) |
|---|---|---|
| `department` | exatamente 1 | `calcado`, `vestuario`, `acessorio`, `equipamento`, `nutricao` |
| `sports` | 1 a 2 | `corrida`, `futebol`, `basquete`, `volei`, `natacao`, `ciclismo`, `musculacao`, `yoga`, `luta`, `trilha`, `raquete` |
| `audience` | exatamente 1 | `masculino`, `feminino`, `unissex`, `infantil` |
| `colors` | 0 a 2 | `preto`, `branco`, `cinza`, `azul`, `vermelho`, `verde`, `amarelo`, `laranja`, `rosa`, `roxo`, `multicolor` |
| `free` | 1 a 4 | livres (ver §7.3) |

- `colors` aceita 0 para produtos sem cor (ex.: suplementos).
- **Ambiguidade "tênis"**: o esporte entra como `raquete` (tênis, beach tennis, padel, squash); `tenis` fica reservado ao calçado.
- Expor: `BASE_VOCABULARY: Mapping[TagGroup, tuple[str, ...]]` e `group_of(tag) -> TagGroup` (retorna `FREE` se não pertencer ao vocabulário base). As constantes do vocabulário são `tuple`, e o mapeamento é constante de configuração, não estrutura principal.
- Total de tags por produto: **mínimo 4, máximo 10** (1 + 1–2 + 1 + 0–2 + 1–4, menos duplicatas). Isso substitui o "3 a 8" discutido antes do vocabulário por grupos.

### 6.3 Normalização (`utils/text_normalizer.py`)

`normalize_tag(raw: str) -> tuple[str, ...]`, aplicada a **toda tag gerada pela IA**:

1. `lower()` + `strip()`;
2. remove acentos (`unicodedata.normalize("NFKD")` + descarta marcas combinantes);
3. troca qualquer caractere fora de `[a-z0-9]` por espaço;
4. **quebra em palavras** (`"calçado esportivo"` → `("calcado", "esportivo")`);
5. descarta stopwords (`de, da, do, das, dos, para, com, em, e, a, o, as, os, um, uma`);
6. descarta palavras com menos de 2 ou mais de 30 caracteres.

`normalize_tags(raws) -> tuple[str, ...]`: aplica a cada uma e **deduplica preservando a ordem** (deduplicação feita com `HashSet`).

`tokenize_query(query: str) -> tuple[str, ...]`: mesma pipeline aplicada ao texto de busca. Garante que `"Calçado"` encontre `calcado`.

---

## 7. Geração de tags com IA (Gemini)

Local: `services/tag_generator.py`, classe `GeminiTagGenerator`.

### 7.1 Integração

| Item | Decisão |
|---|---|
| SDK | `google-genai` (oficial) |
| Modelo | env `GEMINI_MODEL`; padrão = modelo **Flash/Flash-Lite estável do free tier** vigente na implementação (conferir no AI Studio) |
| Saída | **structured output**: `response_mime_type="application/json"` + `response_schema` com `enum` nos grupos fechados |
| Temperatura | 0,2 |
| Timeout | 15 s por tentativa |
| Tentativas | 2 (1 original + 1 retry) em qualquer erro: rede, cota, JSON inválido, validação |
| Falha final | lança `TagGenerationError` → API responde `503` "Serviço de IA indisponível, tente novamente." |
| Fallback por palavras-chave | **não** |

### 7.2 Schema de resposta

```json
{
  "type": "object",
  "properties": {
    "department": { "type": "string", "enum": ["calcado", "vestuario", "acessorio", "equipamento", "nutricao"] },
    "sports":     { "type": "array", "items": { "type": "string", "enum": ["corrida", "..."] }, "minItems": 1, "maxItems": 2 },
    "audience":   { "type": "string", "enum": ["masculino", "feminino", "unissex", "infantil"] },
    "colors":     { "type": "array", "items": { "type": "string", "enum": ["preto", "..."] }, "minItems": 0, "maxItems": 2 },
    "free_tags":  { "type": "array", "items": { "type": "string" }, "minItems": 1, "maxItems": 4 }
  },
  "required": ["department", "sports", "audience", "colors", "free_tags"]
}
```

O schema é **gerado a partir de `BASE_VOCABULARY`**, sem duplicar listas. A resposta também é **revalidada no backend** com um modelo Pydantic privado (`_GeneratedTags`), porque o schema do provedor não é garantia absoluta.

### 7.3 Prompt (rascunho)

**System instruction:**
```
Você classifica produtos de uma loja brasileira de artigos esportivos.
Gere tags para indexar o produto na busca da loja.

Regras:
1. department, sports, audience e colors: use SOMENTE os valores permitidos no schema.
2. colors: lista vazia se o produto não tiver cor definida (ex.: suplementos).
3. free_tags: de 1 a 4 tags, cada uma com UMA palavra, em português, minúsculas,
   no singular e genérica. A primeira deve ser o tipo do produto
   (ex.: tenis, bola, camiseta, shorts, luva, whey, garrafa).
4. Nunca use frases: "tênis de corrida" vira "tenis" (e "corrida" já está em sports).
5. Não repita em free_tags valores já escolhidos nos outros campos.
6. Quando uma destas tags existentes descrever o produto, reutilize-a em vez de criar sinônimo:
   {existing_free_tags}
```

**Conteúdo do usuário:**
```
Nome: {name}
Descrição: {description}
```

- `existing_free_tags` = até **100 tags livres** (grupo `FREE`) mais frequentes no índice, separadas por vírgula; vazio no primeiro cadastro.
- Montagem do prompt em função pura `build_prompt(...)` (testável sem rede).

### 7.4 Pós-processamento

1. Valida com `_GeneratedTags`.
2. Concatena na ordem: `department`, `sports`, `audience`, `colors`, `free_tags`.
3. `normalize_tags(...)` → quebra compostas, remove acentos e stopwords, deduplica.
4. Tags livres excedentes após a quebra: mantém as **4 primeiras** livres.
5. Resultado vazio ou sem `department` → resposta inválida (conta como tentativa falha).

### 7.5 Exemplo

Entrada: `name="Tênis Velocity"`, `description="Tênis azul para corrida em asfalto, amortecimento leve"`

Saída do Gemini:
```json
{"department": "calcado", "sports": ["corrida"], "audience": "unissex",
 "colors": ["azul"], "free_tags": ["tenis", "asfalto", "amortecimento"]}
```
Tags finais: `("calcado", "corrida", "unissex", "azul", "tenis", "asfalto", "amortecimento")`

---

## 8. Índice em memória e busca

Local: `services/catalog_index.py`, classe `CatalogIndex`.

### 8.1 Estado

| Atributo | Tipo | Conteúdo |
|---|---|---|
| `_products` | `HashTable[int, Product]` | id → produto |
| `_tag_index` | `HashTable[str, HashSet[int]]` | tag → ids (índice invertido) |
| `_lock` | `threading.RLock` | ver §13 |

Exemplo:
```
_products:   7 → Product("Tênis Velocity", …)     12 → Product("Camiseta Dry", …)
_tag_index:  "azul"    → {7, 12}
             "corrida" → {7}
             "tenis"   → {7}
```

### 8.2 Operações

| Método | Comportamento | Complexidade (média) |
|---|---|---|
| `add(product)` | insere em `_products`; para cada tag, cria o `HashSet` se não existir e adiciona o id | O(t), t = nº de tags |
| `remove(product_id) -> Product` | remove de `_products`; tira o id de cada `HashSet`; **apaga a tag se o set esvaziar**; `ProductNotFoundError` se ausente | O(t) |
| `get(product_id) -> Product` | `ProductNotFoundError` se ausente | O(1) |
| `contains(product_id) -> bool` | | O(1) |
| `search(terms) -> list[SearchHit]` | OR ranqueado (§8.3) | O(q + m + r log r) |
| `list_all() -> list[SearchHit]` | todos, `score=0`, mais recentes primeiro | O(n log n) |
| `tag_counts() -> list[tuple[str, int]]` | tag + tamanho do set, ordenado por contagem desc, depois alfabética | O(T log T) |
| `top_free_tags(limit) -> tuple[str, ...]` | tags do grupo `FREE` mais frequentes (para o prompt) | O(T log T) |
| `__len__` / `tag_total` | nº de produtos / nº de tags distintas | O(1) |

`q` = termos da busca, `m` = soma dos ids encontrados, `r` = nº de resultados, `T` = tags distintas.

`SearchHit` = `@dataclass(frozen=True)` com `product: Product`, `score: int`, `matched_tags: tuple[str, ...]` (definido em `services/catalog_index.py`).

### 8.3 Algoritmo de busca (OR ranqueado)

```python
def search(self, terms: tuple[str, ...]) -> list[SearchHit]:
    scores = HashTable[int, int]()                  # id → nº de termos que bateram
    matched = HashTable[int, tuple[str, ...]]()     # id → termos que bateram
    for term in terms:
        ids = self._tag_index.get(term)
        if ids is None:
            continue                                # termo irrelevante: não pontua
        for product_id in ids:
            scores[product_id] = scores.get(product_id, 0) + 1
            matched[product_id] = matched.get(product_id, ()) + (term,)
    hits = (SearchHit(self._products[pid], scores[pid], matched[pid]) for pid in scores)
    return sorted(hits, key=lambda h: (-h.score, -h.product.id))
```

Regras:
- Só aparecem produtos com `score ≥ 1`.
- Ordenação: **mais termos casados primeiro**; empate → **id maior (mais recente) primeiro**.
- Busca vazia (`q` ausente ou só espaços) → `list_all()`.
- `q` não vazio mas sem termos válidos após a normalização (ex.: `"para"`) → lista vazia.
- O placar é uma `HashTable` própria (estrutura principal), não `dict`. O `sorted()` final só produz a resposta.

### 8.4 Fora do escopo da busca

Prefixo/parcial (`tên` → `tenis`), busca no texto da descrição, sinônimos, paginação, AND explícito.

---

## 9. API HTTP

FastAPI. Erros no formato padrão `{"detail": "..."}` com mensagens em pt-BR.

### 9.1 Rotas

| Método | Rota | Entrada | Sucesso | Erros |
|---|---|---|---|---|
| GET | `/health` | — | `200 HealthResponse` | — |
| POST | `/api/products` | `ProductCreateRequest` | `201 ProductResponse` | `422` validação · `503` IA indisponível · `500` banco |
| GET | `/api/products` | `q` opcional (máx. 200 caracteres) | `200 list[SearchResultResponse]` | `422` se `q` > 200 |
| GET | `/api/products/{id}` | — | `200 ProductResponse` | `404` |
| DELETE | `/api/products/{id}` | header `X-Admin-Key` | `204` | `401` chave ausente/inválida · `404` · `500` banco |
| GET | `/api/tags` | — | `200 list[TagCountResponse]` | — |

`/health` fica fora de `/api`: é o health check do Render, o alvo do keep-alive e o "despertador" do front.

### 9.2 Schemas (`schemas/`, um por arquivo)

```python
# product_create.py
class ProductCreateRequest(BaseModel):
    name: str          # strip; 2..120
    description: str   # strip; 10..1000

# product_response.py
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    tags: list[str]
    created_at: datetime

    @classmethod
    def from_entity(cls, product: Product) -> "ProductResponse"

# search_result.py
class SearchResultResponse(BaseModel):
    product: ProductResponse
    score: int
    matched_tags: list[str]

# tag_count.py
class TagCountResponse(BaseModel):
    tag: str
    count: int
    group: TagGroup

# health.py
class HealthResponse(BaseModel):
    status: Literal["ok"]
    products: int
    tags: int
    gemini_configured: bool
```

### 9.3 Exemplos

```http
POST /api/products
{"name": "Tênis Velocity", "description": "Tênis azul para corrida em asfalto, amortecimento leve"}

201
{"id": 7, "name": "Tênis Velocity", "description": "...",
 "tags": ["calcado","corrida","unissex","azul","tenis","asfalto","amortecimento"],
 "created_at": "2026-11-21T18:02:11Z"}
```

```http
GET /api/products?q=tenis%20azul%20futebol

200
[{"product": {...id 7...},  "score": 2, "matched_tags": ["tenis","azul"]},
 {"product": {...id 12...}, "score": 1, "matched_tags": ["azul"]}]
```

```http
GET /api/tags
200
[{"tag": "corrida", "count": 5, "group": "sports"},
 {"tag": "tenis",   "count": 3, "group": "free"}, ...]
```

### 9.4 Mapeamento de exceções (`exceptions.py` + handlers em `main.py`)

| Exceção de domínio | HTTP |
|---|---|
| `ProductNotFoundError` | 404 "Produto não encontrado." |
| `TagGenerationError` | 503 "Serviço de IA indisponível, tente novamente." |
| `PersistenceError` | 500 "Erro ao acessar o banco de dados." |
| chave admin inválida (em `dependencies.py`) | 401 "Chave de administrador inválida." |

---

## 10. Persistência (Supabase / Postgres)

### 10.1 Migração (`supabase/migrations/001_create_products.sql`)

```sql
create table if not exists products (
  id          bigint generated always as identity primary key,
  name        text not null check (char_length(name) between 2 and 120),
  description text not null check (char_length(description) between 10 and 1000),
  tags        text[] not null,
  created_at  timestamptz not null default now()
);

-- RLS ligado e SEM policies: bloqueia acesso pela API REST pública do Supabase (anon).
-- O backend conecta como `postgres`, que ignora RLS.
alter table products enable row level security;
```

- Em **produção**: aplicada manualmente no SQL Editor do Supabase (passo a passo no README).
- Em **dev**: aplicada automaticamente pelo container Postgres (`/docker-entrypoint-initdb.d`).
- O mesmo arquivo serve aos dois ambientes (Postgres puro).

### 10.2 `ProductRepository` (`repositories/product_repository.py`)

psycopg 3, SQL puro, `psycopg_pool.ConnectionPool` (min 1, máx 3).

| Método | SQL | Retorno |
|---|---|---|
| `insert(name, description, tags)` | `INSERT … RETURNING id, created_at` | `Product` |
| `delete(product_id)` | `DELETE … WHERE id = %s` | `bool` (linha afetada) |
| `load_all()` | `SELECT id, name, description, tags, created_at FROM products ORDER BY id` | `Iterator[Product]` |

Erros do psycopg são encapsulados em `PersistenceError`.

### 10.3 Conexão

- Produção: **Session pooler** do Supabase (IPv4, porta 5432). O Render não alcança o endereço IPv6 da conexão direta, e o Transaction pooler (6543) quebra os prepared statements do psycopg.
- Dev: `postgresql://postgres:postgres@db:5432/catalog` (container local).

---

## 11. Backend: estrutura e responsabilidades

### 11.1 Árvore

```
backend/
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── .python-version                 # 3.12
├── app/
│   ├── main.py                     # cria app, CORS, lifespan, handlers de exceção
│   ├── config.py                   # Settings (pydantic-settings)
│   ├── dependencies.py             # providers de Depends + verificação X-Admin-Key
│   ├── exceptions.py               # ProductNotFoundError, TagGenerationError, PersistenceError
│   │
│   ├── data_structures/            # ★ genérico; não importa nada do app
│   │   ├── linked_list.py          # Node + LinkedList
│   │   ├── hash_table.py           # HashTable
│   │   └── hash_set.py             # HashSet
│   │
│   ├── models/                     # entidades e regras de domínio
│   │   ├── product.py              # Product
│   │   └── tag_vocabulary.py       # TagGroup, BASE_VOCABULARY, group_of
│   │
│   ├── schemas/                    # contratos HTTP (Pydantic), 1 por arquivo
│   │   ├── product_create.py
│   │   ├── product_response.py
│   │   ├── search_result.py
│   │   ├── tag_count.py
│   │   └── health.py
│   │
│   ├── routes/                     # endpoints, só HTTP
│   │   ├── health.py
│   │   ├── products.py
│   │   └── tags.py
│   │
│   ├── services/
│   │   ├── catalog_index.py        # CatalogIndex + SearchHit
│   │   ├── catalog_service.py      # CatalogService (orquestração)
│   │   └── tag_generator.py        # GeminiTagGenerator, build_prompt, schema
│   │
│   ├── repositories/
│   │   └── product_repository.py   # ProductRepository
│   │
│   └── utils/
│       └── text_normalizer.py      # normalize_tag, normalize_tags, tokenize_query
│
└── tests/                          # espelha app/
    ├── conftest.py                 # fakes: FakeTagGenerator, InMemoryProductRepository
    ├── data_structures/
    ├── models/
    ├── services/
    ├── utils/
    └── routes/
```

### 11.2 Regras de dependência

```
routes ──▶ services ──▶ data_structures
   │          │  └────▶ models, utils
   ▼          ▼
schemas    repositories / tag_generator  (injetados no CatalogService)
```

- `data_structures/` não importa nada do app.
- `CatalogIndex` usa só `data_structures`, `models` e `utils`: **sem I/O**.
- `CatalogService` é o único que conhece gerador de tags + repositório + índice.
- `routes` só conversam com `CatalogService` (via `Depends`) e `schemas`.
- Gerador de tags e repositório são **injetados** no `CatalogService` (duck typing; os testes usam fakes).

### 11.3 `CatalogService` (`services/catalog_service.py`)

```python
class CatalogService:
    def __init__(self, index: CatalogIndex, repository: ProductRepository, tag_generator: GeminiTagGenerator)

    def load_index(self) -> int                                   # startup; retorna nº carregado
    def create_product(self, name: str, description: str) -> Product
    def get_product(self, product_id: int) -> Product
    def delete_product(self, product_id: int) -> None
    def search(self, query: str | None) -> list[SearchHit]
    def list_tags(self) -> list[tuple[str, int, TagGroup]]
    def stats(self) -> tuple[int, int]                            # (produtos, tags) para /health
```

### 11.4 Configuração (`config.py`)

```python
class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str = ""
    gemini_model: str = "<flash-free-tier>"
    admin_key: str = ""
    allowed_origins: list[str] = ["http://localhost:8080"]
    log_level: str = "INFO"
```

### 11.5 Tooling

| Item | Decisão |
|---|---|
| Python | 3.12 |
| Gerenciador | `uv` (`pyproject.toml` + `uv.lock`) |
| Runtime | `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `google-genai`, `psycopg[binary,pool]` |
| Dev | `pytest`, `httpx`, `ruff` |
| Lint/format | `ruff check` + `ruff format`, linha de 100, regras `E,F,I,B,UP,N,SIM` |
| Tipagem | type hints em todas as assinaturas públicas |
| Logging | `logging` padrão, INFO, mensagens em inglês |

---

## 12. Frontend

### 12.1 Stack

HTML + **JavaScript vanilla com ES modules**, sem build e sem framework. **Pico.css** via CDN (versão fixada) + `styles.css` com ajustes finos. UI em pt-BR.

### 12.2 Estrutura

```
frontend/
├── index.html
├── css/
│   └── styles.css
└── js/
    ├── main.js               # inicializa e conecta os componentes
    ├── config.js             # URL da API
    ├── api.js                # ÚNICO módulo que faz fetch
    └── components/
        ├── server-status.js  # banner de cold start
        ├── product-form.js   # cadastro
        ├── search-bar.js     # busca com debounce
        ├── tag-filters.js    # chips por grupo
        ├── product-list.js   # grid de cards
        └── admin-panel.js    # chave admin
```

Regras:
- Cada componente exporta `mount(element, options)`; sem classes nem estado global.
- Componentes se comunicam por **callbacks** passados em `main.js`.
- Só `api.js` conhece URLs e `fetch`.

### 12.3 `config.js`

```js
const LOCAL_HOSTS = ["localhost", "127.0.0.1"];
export const API_BASE_URL = LOCAL_HOSTS.includes(window.location.hostname)
  ? "http://localhost:8000"
  : "https://<servico>.onrender.com";
```

### 12.4 `api.js`

- `getHealth()`, `listProducts(query)`, `getProduct(id)`, `createProduct({name, description})`, `deleteProduct(id, adminKey)`, `listTags()`.
- Timeout via `AbortController`: **90 s** (cobre cold start do Render + chamada à IA).
- Erro HTTP → lança `ApiError {status, message}`. `422` do FastAPI (array de erros) é convertido em texto legível.

### 12.5 Layout e comportamento

```
┌──────────────────────────────────────────────────────────────────┐
│ Catálogo Esportivo                        [banner cold start]    │
├───────────────────────┬──────────────────────────────────────────┤
│ Cadastrar produto     │ [ buscar…                            ]   │
│ Nome  [            ]  │ Departamento: (calcado)(vestuario)…      │
│ Descrição          ]  │ Esporte: (corrida)(futebol)…             │
│ [   Gerar tags e   ]  │ Público: …   Cor: …                      │
│ [     salvar       ]  │ ┌────────┐ ┌────────┐ ┌────────┐         │
│                       │ │ card   │ │ card   │ │ card   │         │
│ ✓ produto criado      │ │ tags   │ │ tags   │ │ tags   │         │
│   com tags            │ └────────┘ └────────┘ └────────┘         │
├───────────────────────┴──────────────────────────────────────────┤
│ rodapé: [chave admin ••••] [salvar]                              │
└──────────────────────────────────────────────────────────────────┘
```

| Componente | Comportamento |
|---|---|
| `server-status` | ao abrir, chama `/health`; se não responder em 2 s, mostra "Acordando servidor, pode levar até 1 minuto…"; some quando responde; em erro, mostra mensagem e botão "tentar de novo" |
| `product-form` | valida tamanhos no cliente; botão desabilitado + "IA gerando tags…" durante o POST; sucesso mostra o produto com as tags e avisa a lista e os filtros para recarregar; erro mostra a mensagem do `ApiError` |
| `search-bar` | debounce de 300 ms → `listProducts(q)` |
| `tag-filters` | carrega `/api/tags`; mostra só grupos **base** (Departamento, Esporte, Público, Cor), cada chip com contagem; clicar adiciona/remove o termo no campo de busca |
| `product-list` | grid de cards: nome, descrição truncada (~140 caracteres), todas as tags; **tags em `matched_tags` destacadas**; estado vazio ("Nenhum produto encontrado"); botão excluir só se houver chave admin |
| `admin-panel` | campo de senha + salvar; guarda no `localStorage` (com try/catch); ao salvar, os cards passam a exibir "excluir"; `401` na exclusão apaga a chave salva e avisa |

Responsivo: 2 colunas no desktop, empilhado no mobile (grid do Pico).

---

## 13. Concorrência e consistência

| Item | Decisão |
|---|---|
| Workers | **exatamente 1** worker uvicorn (fixado no `Dockerfile`, documentado). Com mais de 1, cada processo teria seu próprio índice e os dados divergiriam |
| Lock | `threading.RLock` **dentro do `CatalogIndex`**; todos os métodos públicos (leitura e escrita) o adquirem |
| `data_structures/` | sem lock (como `dict`) |
| Chamada à IA | **fora** do lock |
| Ordem no cadastro | IA → `INSERT` → `index.add`. Falha no banco = nada indexado |
| Ordem na exclusão | checa existência no índice → `DELETE` → `index.remove`. Falha no banco = índice intacto |
| Divergência residual | se `index.add` falhasse após o `INSERT` (improvável), o produto reaparece no próximo restart (rebuild). Aceito no MVP, com log de erro |

---

## 14. Segurança

| Item | Decisão |
|---|---|
| Leitura e cadastro | públicos |
| Exclusão | header `X-Admin-Key` comparado com `ADMIN_KEY` via `secrets.compare_digest`; se `ADMIN_KEY` vazia, exclusão sempre `401` |
| CORS | `ALLOWED_ORIGINS` (Netlify + `http://localhost:8080`); métodos `GET, POST, DELETE`; headers `Content-Type, X-Admin-Key` |
| Banco | RLS ligado sem policies; credenciais só no Render |
| Segredos | `.env` fora do git; `.env.example` versionado; `ADMIN_KEY` gerada pelo Render |
| Entrada | limites de tamanho (Pydantic + `CHECK` no banco); `q` ≤ 200 caracteres |
| Prompt injection | mitigado por structured output com `enum` + normalização das tags livres (só `[a-z0-9]`) |
| Rate limit | não; a cota do Gemini é o limite natural |

---

## 15. Ambiente de desenvolvimento (Docker)

### 15.1 `docker-compose.yml`

| Serviço | Imagem | Porta | Detalhes |
|---|---|---|---|
| `api` | `backend/Dockerfile`, target `dev` | 8000 | `uvicorn --reload`; volumes `./backend/app` e `./backend/tests`; `env_file: .env`; `DATABASE_URL` apontando para `db`; `depends_on: db (healthy)` |
| `db` | `postgres:16-alpine` | 5432 | volume `pgdata`; `./supabase/migrations` montado em `/docker-entrypoint-initdb.d:ro`; healthcheck `pg_isready` |
| `web` | `nginx:alpine` | 8080 | `./frontend` montado em `/usr/share/nginx/html:ro` |

### 15.2 `backend/Dockerfile` (multi-stage)

| Stage | Conteúdo |
|---|---|
| `base` | `python:3.12-slim` + binário do `uv` (imagem oficial, versão fixada) + `uv sync --frozen --no-dev` |
| `dev` | `uv sync --frozen` (com dev deps); `CMD uvicorn … --reload` |
| `prod` (**último**, padrão) | copia `app/`; `CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1` |

O pipeline (§17.2) constrói explicitamente `--target prod` e publica a imagem; o Render só a executa. Dev e produção usam o mesmo Dockerfile.

### 15.3 `Makefile`

| Alvo | Comando |
|---|---|
| `make up` | `docker compose up -d --build` |
| `make down` | `docker compose down` |
| `make logs` | `docker compose logs -f api` |
| `make test` | `docker compose run --rm api pytest` |
| `make lint` | `docker compose run --rm api sh -c "ruff check . && ruff format --check ."` |
| `make format` | `docker compose run --rm api ruff format .` |
| `make reset-db` | `docker compose down -v` (apaga o volume e reaplica a migração no próximo `up`) |

### 15.4 Variáveis (`.env.example` na raiz)

```dotenv
GEMINI_API_KEY=
GEMINI_MODEL=
ADMIN_KEY=dev-admin-key
ALLOWED_ORIGINS=http://localhost:8080
LOG_LEVEL=INFO
# DATABASE_URL é definida pelo docker-compose em dev
```

Em dev, o Gemini é **real** (exige `GEMINI_API_KEY` no `.env`).

---

## 16. Testes e CI/CD

### 16.1 Estratégia

| Alvo | O que testar | Técnica |
|---|---|---|
| `data_structures/linked_list` | inserir, achar, remover (cabeça/meio/fim/ausente), iterar, len | casos diretos |
| `data_structures/hash_table` | put/get/sobrescrever/remove/contains/len/iteração, `KeyError`, default do `get`, resize (capacidade dobra, nada se perde), colisões | **oráculo `dict`**: 10 000 operações aleatórias (seed fixa) aplicadas nas duas e comparadas a cada passo; **`CollidingKey`** com `__hash__` constante força todas as chaves no mesmo bucket |
| `data_structures/hash_set` | add/remove/discard/contains/len/iteração | oráculo `set` |
| `utils/text_normalizer` | acentos, caixa, símbolos, quebra de compostas, stopwords, limites, dedupe | `parametrize` |
| `models/tag_vocabulary` | 31 tags, sem duplicatas entre grupos, `group_of` | diretos |
| `services/catalog_index` | add/remove (tag some ao esvaziar), get, ranking OR, empate por id, busca vazia, termo inexistente, `tag_counts`, `top_free_tags` | puro |
| `services/tag_generator` | `build_prompt`, validação/normalização, truncamento de livres, retry, `TagGenerationError` após 2 falhas | client do Gemini mockado, **sem rede** |
| `services/catalog_service` | cadastro feliz; IA falha → nada salvo; banco falha → nada indexado; exclusão; `load_index` | `FakeTagGenerator` + `InMemoryProductRepository` |
| `routes` | status codes, contrato JSON, `X-Admin-Key`, `422`, `404`, `503` | `TestClient` + `dependency_overrides` |

- **Nenhum teste depende do valor de `hash()`**; `PYTHONHASHSEED=0` no CI só por reprodutibilidade.
- **TDD** em `data_structures/` (teste antes do código).
- Chamadas reais ao Gemini/Supabase não entram nos testes automatizados.
- `scripts/smoke_test.py`: script manual que cadastra, busca e exclui contra uma URL informada (local ou Render).

### 16.2 CI (`.github/workflows/ci.yml`)

Gatilhos: `push` e `pull_request`. Job em `backend/`:
1. `astral-sh/setup-uv` (versão fixada)
2. `uv sync --frozen`
3. `uv run ruff check .`
4. `uv run ruff format --check .`
5. `PYTHONHASHSEED=0 uv run pytest`

Badge do CI no README.

Em `push` na `main`, o mesmo workflow continua com os jobs de deploy (§17.2). Em PR e em outras branches, só o job de lint/testes roda.

---

## 17. Deploy e produção

### 17.1 Serviços

**Princípio:** o único caminho do código até a produção é o `ci.yml`. Render e Netlify **não observam o repositório**; só executam o que o pipeline entrega. Assim, cada deploy é rastreável: commit → run do Actions → imagem `:<sha>` → deploy.

| Serviço | Configuração |
|---|---|
| **GitHub Actions** | `ci.yml` único: lint/testes → deploy da API → deploy do front; ambiente `production` com os secrets de deploy |
| **GHCR** | registro da imagem do backend, `ghcr.io/gabriel-barata/tfinal-produtos-com-tags-automaticas-api`, pacote **público** (o Render puxa sem credencial) |
| **Render** | Web Service **imagem** (`runtime: image`), plano Free, `render.yaml` versionado, `autoDeploy: false`, `healthCheckPath: /health` |
| **Netlify** | `netlify.toml` com `publish = "frontend"`, sem build command; site **sem vínculo com Git** (publicação só via CLI) |
| **Supabase** | projeto Free, Session pooler; migração aplicada manualmente |

### 17.2 Pipeline de deploy (`.github/workflows/ci.yml`)

```
push na main:   backend (lint + testes) ──▶ deploy-api ──▶ deploy-web
PR / branches:  backend (lint + testes)
```

Os jobs de deploy só rodam em `push` na `main`, dependem do job anterior (`needs`) e usam `environment: production` e `concurrency: deploy-production` (`cancel-in-progress: false`, deploys em fila).

| Job | Passos |
|---|---|
| `deploy-api` | login no GHCR com `GITHUB_TOKEN` (`permissions: packages: write`) → `docker/build-push-action` com `target: prod`, tags `:<sha>` e `:latest` → `curl -fsS -X POST` no deploy hook do Render com `imgURL` apontando para `:<sha>` → aguarda `$BACKEND_URL/health` responder (`curl --fail --retry`) |
| `deploy-web` | `netlify-cli` (versão fixada) `deploy --prod --dir=frontend`, com `NETLIFY_AUTH_TOKEN` e `NETLIFY_SITE_ID` |

- O front só é publicado depois de a API responder, para nunca apontar para um backend que não subiu.
- A espera por `/health` é uma verificação de sanidade: durante a troca, a instância antiga pode responder. Se o deploy falhar, o Render mantém a versão anterior no ar e o job fica vermelho.
- O smoke test (§16.1) continua manual.

### 17.3 `render.yaml` (esboço)

```yaml
services:
  - type: web
    name: catalogo-esportivo-api
    runtime: image
    plan: free
    image:
      url: ghcr.io/gabriel-barata/tfinal-produtos-com-tags-automaticas-api:latest
    healthCheckPath: /health
    autoDeploy: false   # deploy só pelo pipeline (deploy hook)
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: GEMINI_MODEL
        value: <flash-free-tier>
      - key: ADMIN_KEY
        generateValue: true
      - key: ALLOWED_ORIGINS
        sync: false
```

### 17.4 Variáveis e secrets de produção

**No Render** (a aplicação):

| Var | Exemplo | Tipo |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres.<ref>:<senha>@aws-0-<região>.pooler.supabase.com:5432/postgres` | secret |
| `GEMINI_API_KEY` | `AIza…` | secret |
| `GEMINI_MODEL` | Flash do free tier | config |
| `ADMIN_KEY` | gerada pelo Render | secret |
| `ALLOWED_ORIGINS` | `https://<site>.netlify.app` | config |

**No GitHub** (o pipeline; ambiente `production`):

| Nome | Tipo | Uso |
|---|---|---|
| `RENDER_DEPLOY_HOOK_URL` | secret | dispara o deploy da imagem no Render |
| `NETLIFY_AUTH_TOKEN` | secret | token pessoal do Netlify |
| `NETLIFY_SITE_ID` | secret | site do front |
| `BACKEND_URL` | variable | URL da API (espera de `/health` e keep-alive) |

Credenciais do banco e do Gemini **não** passam pelo GitHub: ficam só no Render.

### 17.5 Comportamento operacional

- **Fail fast** no startup se o banco estiver inacessível.
- **Cold start**: o Render hiberna após ~15 min sem tráfego; o front trata com banner (§12.5).
- **Keep-alive** (`.github/workflows/keep-alive.yml`): cron a cada 3 dias (`0 12 */3 * *`), `curl --retry 5 --max-time 90 "$BACKEND_URL/health"`. Impede o Supabase free de pausar por inatividade (~7 dias) antes da correção.
  - Limitação: o GitHub desativa workflows agendados após 60 dias sem atividade no repositório, o que não afeta o prazo.

### 17.6 Ordem do primeiro deploy

1. Criar projeto Supabase → rodar `001_create_products.sql` → copiar a URL do Session pooler.
2. Criar chave no Google AI Studio.
3. Netlify: criar o site **sem Git** (deploy manual) → anotar `NETLIFY_SITE_ID` e a URL; gerar `NETLIFY_AUTH_TOKEN`.
4. Merge do PR com `ci.yml`, `render.yaml` e `netlify.toml`. O primeiro run publica a imagem no GHCR; os jobs de deploy falham por falta de secrets (esperado). Tornar o pacote **público** (uma vez).
5. Render: novo Blueprint a partir do repo → preencher secrets e `ALLOWED_ORIGINS` (URL do Netlify) → copiar o deploy hook.
6. GitHub: cadastrar `RENDER_DEPLOY_HOOK_URL`, `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID` (ambiente `production`) e a variable `BACKEND_URL`.
7. Atualizar `API_BASE_URL` em `frontend/js/config.js` com a URL do Render → PR → merge (dispara o primeiro deploy completo).
8. Rodar `scripts/smoke_test.py` contra produção.

---

## 18. Convenções de código, idioma e Git

### 18.1 Idioma por artefato

| Artefato | Idioma |
|---|---|
| Identificadores (classes, métodos, variáveis, arquivos, pastas) | **inglês** |
| Comentários e docstrings | **pt-BR** |
| README e `docs/` | pt-BR |
| Mensagens de erro da API | pt-BR |
| Textos da UI | pt-BR |
| Tags | pt-BR sem acento |
| Commits | inglês, Conventional Commits |
| Logs | inglês |

### 18.2 Estilo

- Uma classe principal por arquivo (exceção: `Node` + `LinkedList`; `CatalogIndex` + `SearchHit`).
- Docstring em toda classe e método público; nas estruturas, sempre com Big-O.
- Comentários explicam **por quê**, não o quê.
- Sem código morto, sem `print` (usar `logging`).

### 18.3 Git

| Item | Regra |
|---|---|
| Repositório | público, `tfinal-produtos-com-tags-automaticas`, conta `gabriel-barata` |
| `main` | sempre deployável; sem push direto; CI obrigatório para merge; todo push na `main` com CI verde é deployado pelo pipeline (§17.2) |
| Branches | 1 por card do Trello: `feat/<n>-slug`, `fix/<n>-slug`, `chore/<n>-slug`, `docs/<n>-slug`, `test/<n>-slug` |
| Merge | PR → CI verde → **squash merge** |
| PR | descrição curta + link do card + checklist de critérios de aceite |
| Release | tag `v1.0.0` no commit entregue |

---

## 19. Documentação entregue (README)

Conteúdo mínimo do `README.md` (pt-BR):

1. Título, badge do CI, links do site (Netlify) e da API (Render).
2. O que o projeto faz (enunciado em 3 linhas) + GIF/screenshot opcional.
3. Arquitetura (diagrama da §4.1).
4. **Estruturas de dados**: explicação da §5.1, decisões da §5.2, **tabela de complexidade**:

| Operação | Média | Pior caso |
|---|---|---|
| `HashTable.put` | O(1) amortizado | O(n) |
| `HashTable.get` / `contains` / `remove` | O(1) | O(n) |
| `HashTable._resize` | O(n) | O(n) |
| Iteração | O(n + capacidade) | O(n + capacidade) |
| `CatalogIndex.add` / `remove` | O(t) | O(t·n) |
| `CatalogIndex.search` | O(q + m + r log r) | — |
| Rebuild no startup | O(N·t) | — |

5. Por que Gemini e não Ollama (§2.3).
6. Como rodar localmente: pré-requisitos (Docker, chave Gemini), `cp .env.example .env`, `make up`, URLs locais, `make test`.
7. Como fazer deploy (§17.6).
8. Variáveis de ambiente.
9. Estrutura de pastas (§11.1, resumida).
10. Link para `docs/SPEC.md`.

---

## 20. Critérios de aceite do MVP

### 20.1 Funcionais

| # | Dado / Quando / Então |
|---|---|
| CA1 | **Dado** nome e descrição válidos, **quando** cadastro, **então** recebo `201` com 4–10 tags normalizadas, incluindo exatamente 1 `department`, 1–2 `sports` e 1 `audience` |
| CA2 | **Dado** um produto cadastrado com a tag `corrida`, **quando** busco "Corrida", **então** ele aparece com `matched_tags = ["corrida"]` |
| CA3 | **Dado** produtos A (`tenis`, `azul`) e B (`azul`), **quando** busco "tênis azul", **então** A vem antes de B (score 2 > 1) |
| CA4 | **Dado** empate de score, **então** o produto mais recente vem primeiro |
| CA5 | **Quando** busco vazio, **então** recebo todos, mais recentes primeiro |
| CA6 | **Quando** busco só termos inexistentes, **então** recebo lista vazia |
| CA7 | **Dado** Gemini indisponível, **quando** cadastro, **então** recebo `503` e nada é gravado no banco nem no índice |
| CA8 | **Dado** chave admin válida, **quando** excluo, **então** recebo `204`, o produto some da busca e tags exclusivas dele somem de `/api/tags` |
| CA9 | **Dado** chave ausente ou errada, **quando** excluo, **então** recebo `401` e nada muda |
| CA10 | **Dado** produtos no banco, **quando** o backend reinicia, **então** busca e `/api/tags` retornam os mesmos resultados de antes |
| CA11 | **Quando** abro o site com o backend hibernado, **então** vejo o banner de cold start e depois o catálogo |
| CA12 | `/api/tags` retorna cada tag com `count` correto e `group` correto |

### 20.2 Técnicos

| # | Critério |
|---|---|
| CT1 | Nenhum `dict`, `set`, `list` ou `collections.*` como armazenamento em `data_structures/` ou `services/catalog_index.py` (revisão manual + grep no PR) |
| CT2 | CI verde (ruff + pytest) na `main` |
| CT3 | `make up` sobe o ambiente completo do zero com `.env` preenchido |
| CT4 | Site no Netlify + API no Render + banco no Supabase funcionando ponta a ponta (`smoke_test.py`) |
| CT7 | Push na `main` com CI verde publica API e site sem passo manual; Render e Netlify não têm auto-deploy próprio |
| CT5 | Docstrings pt-BR com Big-O em todos os métodos públicos das estruturas |
| CT6 | README completo conforme §19 |

---

## 21. Riscos e mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Avaliador exigir Ollama literalmente (rubrica, 20%) | nota de integração | justificativa explícita no README (§2.3) |
| Cota/limite do Gemini free | cadastros falham (503) | retry único; mensagem clara; nenhum dado inconsistente |
| Modelo Gemini descontinuado | cadastros falham | `GEMINI_MODEL` configurável por env |
| Supabase free pausa por inatividade | backend não sobe (fail fast) | keep-alive a cada 3 dias |
| Deploy falha depois do merge (roda após o CI) | `main` com versão pendente | Render mantém a versão anterior; job vermelho; re-run do workflow |
| Cold start do Render (~50 s) | primeira impressão lenta | banner no front; timeout de 90 s |
| Corrida de threads no índice | corrupção da HashTable | `RLock` no `CatalogIndex`, 1 worker |
| Meta de terminar o código em 1 dia | escopo não concluído | MVP enxuto; cards pequenos com dependências explícitas; a `main` sempre deployável |
| Uso acidental de `dict`/`list` na estrutura principal | perda de nota (70%) | política §2.2 + CT1 + revisão no PR |

---

## 22. Marcos

| Data | Marco |
|---|---|
| 21/11/2026 | spec aprovada → cards no Trello → **código completo e deployado** |
| até 03/12/2026 | revisão final, README, smoke test em produção, tag `v1.0.0` |
| **04/12/2026** | **entrega ao professor** (link do repositório) |

---

## 23. Registro de decisões

| ID | Decisão | Alternativas descartadas | Motivo |
|---|---|---|---|
| D01 | Começar do zero; repo do professor só como referência de deploy | fork do `projeto1` | é o P1 (helpdesk), sem estrutura de dados reaproveitável, código defensivo/ofuscado, acoplado ao domínio |
| D02 | Gemini direto (free tier) | Ollama local; Ollama + Gemini via abstração; Groq/OpenRouter | integração fácil, documentação ampla, usado nos guias do professor, custo zero; Ollama inviável no Render free |
| D03 | Supabase só como persistência; índice em memória reconstruído no startup; busca 100% na HashTable | sem banco (JSON/seed); banco fazendo a busca | Render hiberna e zera memória; mantém a estrutura como motor da busca (70%) |
| D04 | `HashTable`/`HashSet`/`LinkedList` próprias com interface estilo dict; `dict` como oráculo nos testes | usar `dict`; perguntar ao professor | "Regra de Ouro" + 70% da nota; a interface dict-like mantém o código idiomático |
| D05 | Encadeamento, `hash()` builtin, capacidade 8, resize ×2 com carga > 0,75, sem shrink | endereçamento aberto; FNV-1a próprio; contadores de estatística | simplicidade e legibilidade; built-ins liberados |
| D06 | Identificadores em inglês; classe chama `HashTable` | nomes em pt-BR | padrão profissional |
| D07 | `Product(id, name, description, tags: tuple, created_at)` | preço, imagem, estoque, edição de tags | MVP; `tuple` evita discussão sobre `list.append` |
| D08 | Structured output, normalização própria, reuso de tags existentes, 1 retry → 503, sem fallback | parse de markdown; fallback por palavras-chave | robustez e consistência do vocabulário |
| D09 | Tags de uma palavra; compostas são quebradas | hífen (`calcado-esportivo`) | a busca por uma palavra precisa casar a chave exata |
| D10 | Busca OR ranqueada, empate por mais recente | AND; prefixo | AND devolve vazio com facilidade; prefixo exige outra estrutura |
| D11 | Vocabulário híbrido: grupos fechados com `enum` + 1–4 livres | só livre; só fechado | consistência + busca por tipo de produto (`tenis`) |
| D12 | Domínio: artigos esportivos; esporte "tênis" = `raquete` | loja geral | vocabulário controlável; resolve a colisão semântica |
| D13 | Operações: cadastrar, buscar/listar, obter, tags, excluir | editar, regerar tags, lote | excluir exercita `remove` de ponta a ponta |
| D14 | Leitura/cadastro públicos; excluir com `X-Admin-Key` | sem proteção; Supabase Auth | protege o destrutivo com custo mínimo |
| D15 | 6 rotas; busca em `GET /api/products?q=`; `/health` fora de `/api` | rota `/search` separada | busca vazia = listagem |
| D16 | Diferenciais: só Big-O documentado + Docker | raio-X da HashTable, benchmark, seed, vídeo | avaliados como sem valor para o objetivo |
| D17 | Front vanilla ES modules + Pico.css, componentes em arquivos | React/Vite/TS; `app.js` único | uma tela; revisável sem experiência em front; sem build |
| D18 | Backend em 7 pastas por camada, 1 classe por arquivo, sem subpastas | 2 pastas genéricas; ~15 pastas aninhadas | equilíbrio entre organização e navegabilidade num MVP |
| D19 | Python 3.12, uv, psycopg 3 + SQL puro, ruff, Session pooler, RLS sem policies | SQLAlchemy; pip/requirements; Transaction pooler; RLS desligado | 1 tabela; lock determinístico; IPv4; segurança |
| D20 | Testes por camada, oráculo + `CollidingKey`, CI no GH Actions | só testes manuais | 70% da nota depende de as operações funcionarem |
| D21 | Docker Compose (api, Postgres local, nginx); mesma imagem no Render | Supabase em dev; runtime Python nativo no Render | paridade dev/prod; dev offline e sem sujar produção |
| D22 | Idiomas: código e commits EN; comentários, docs, UI e erros pt-BR | tudo EN; tudo PT | o avaliador lê pt-BR; o código segue o padrão de mercado |
| D23 | Branch por card, PR + squash, CI obrigatório, tag `v1.0.0` | trunk direto na `main` | histórico limpo, 1 commit por card |
| D24 | Fail fast no startup; keep-alive a cada 3 dias | subir degradado; sem keep-alive | evita índice vazio silencioso; evita pausa do Supabase |
| D25 | 1 worker; `RLock` no `CatalogIndex`; IA fora do lock | lock na `HashTable`; vários workers | estruturas puras; índice único e consistente |
| D26 | Deploy centralizado no `ci.yml`: build da imagem `prod` → GHCR → deploy hook do Render; Netlify via CLI; `autoDeploy` desligado nos dois | auto-deploy nativo do Render/Netlify via Git | uma trilha rastreável (commit → run → imagem `:<sha>` → deploy); mesmo artefato testado vai para produção; custo: GHCR + 3 secrets no GitHub |

---

## 24. Fora de escopo / pós-MVP

- Edição de produto e regeneração de tags
- Cadastro em lote / importação CSV
- Busca por prefixo/parcial, sinônimos, busca na descrição, AND explícito
- Paginação, página de detalhe, imagens, preço, estoque
- Autenticação de usuários (além da chave admin)
- Rate limit por IP
- Shrink da HashTable
- Visualização interna da HashTable, benchmark, seed de produtos, vídeo de demo
- Ollama como provedor alternativo
- Dark mode manual
