# 21 · Deploy: Render (API) + Netlify (front)

| Campo | Valor |
|---|---|
| Labels | `infra` |
| Tamanho | M |
| Depende de | 15, 19, 20 |
| Branch | `chore/21-deploy` |

## Objetivo
Aplicação completa no ar, com auto-deploy a partir da `main`.

## Escopo
- [ ] `render.yaml` (SPEC §17.2): Docker, plano free, `healthCheckPath: /health`, env vars
- [ ] `netlify.toml`: `publish = "frontend"`, sem build
- [ ] Render: criar via Blueprint, preencher `DATABASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`; anotar a `ADMIN_KEY` gerada
- [ ] Atualizar `API_BASE_URL` em `frontend/js/config.js` com a URL do Render
- [ ] Netlify: importar o repo, publicar, copiar a URL
- [ ] Definir `ALLOWED_ORIGINS` no Render com a URL do Netlify

## Critérios de aceite
- [ ] `https://<api>.onrender.com/health` → `status: ok`, `gemini_configured: true`
- [ ] Site do Netlify cadastra, busca e exclui em produção
- [ ] Restart manual do serviço no Render preserva o catálogo (CA10)

## Referências
SPEC §17
