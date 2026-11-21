# 20 · Provisionar Supabase e chave Gemini (manual)

| Campo | Valor |
|---|---|
| Labels | `infra`, `manual` |
| Tamanho | P |
| Depende de | 03 |
| Branch | — (sem código) |

## Objetivo
Contas e credenciais de produção prontas.

## Escopo
- [ ] Supabase: novo projeto Free, região São Paulo; anotar a senha do banco
- [ ] Rodar `supabase/migrations/001_create_products.sql` no SQL Editor
- [ ] Copiar a URL do **Session pooler** (porta 5432) e montar a `DATABASE_URL`
- [ ] Google AI Studio: criar a `GEMINI_API_KEY`
- [ ] Guardar as credenciais fora do repositório

## Critérios de aceite
- [ ] Tabela `products` visível no Table Editor com RLS ligado
- [ ] Conexão local de teste com a `DATABASE_URL` do pooler funciona (ex.: `psql`)

## Referências
SPEC §10.3, §17.5 passos 1–2
