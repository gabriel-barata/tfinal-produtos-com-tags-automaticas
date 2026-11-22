# 14 · Wiring da API (DI, lifespan, CORS, erros, /health)

| Campo | Valor |
|---|---|
| Labels | `backend` |
| Tamanho | M |
| Depende de | 13 |
| Branch | `feat/14-api-wiring` |

## Objetivo
Montar a aplicação: injeção de dependências, startup com fail fast, CORS, handlers de exceção e `/health` real.

## Escopo
- [ ] `app/dependencies.py`: providers do `CatalogService` (instância única criada no lifespan, guardada em `app.state`), `require_admin_key` (`secrets.compare_digest`; `ADMIN_KEY` vazia → sempre 401)
- [ ] `app/main.py`: lifespan cria pool + client Gemini + índice + service e chama `load_index`; **falha → exceção não tratada (fail fast)** com log claro; fecha o pool no shutdown
- [ ] CORS com `ALLOWED_ORIGINS`; métodos `GET, POST, DELETE`; headers `Content-Type, X-Admin-Key`
- [ ] Handlers: `ProductNotFoundError` 404, `TagGenerationError` 503, `PersistenceError` 500 (mensagens pt-BR da SPEC §9.4)
- [ ] `app/schemas/health.py` + `app/routes/health.py`: `{status, products, tags, gemini_configured}`
- [ ] `app/routes/__init__` / registro dos routers em `main.py` (prefixo `/api` para products/tags)
- [ ] Logging configurado com `LOG_LEVEL`
- [ ] Testes com `dependency_overrides` (fakes)

## Critérios de aceite
- [ ] `/health` reflete contagens reais do índice
- [ ] Startup com banco inacessível encerra o processo com log claro
- [ ] Preflight CORS de origem não permitida é rejeitado

## Referências
SPEC §9.1, §9.4, §14, §17.5
