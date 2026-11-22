# 21 · Deploy via CI: Render (API) + Netlify (front)

| Campo | Valor |
|---|---|
| Labels | `infra` |
| Tamanho | M |
| Depende de | 04, 15, 19, 20 |
| Branch | `chore/21-deploy` |

## Objetivo
Aplicação completa no ar, publicada **somente** pelo pipeline (`ci.yml`) a cada push na `main`. Render e Netlify não observam o repositório.

## Escopo
- [ ] `ci.yml`: jobs `deploy-api` e `deploy-web` (SPEC §17.2), só em `push` na `main`, `needs` encadeado, `environment: production`, `concurrency: deploy-production`
- [ ] `deploy-api`: login no GHCR, build `target: prod`, push `:<sha>` e `:latest`, `POST` no deploy hook do Render com `imgURL`, espera `/health`
- [ ] `deploy-web`: `netlify-cli` com versão fixada, `deploy --prod --dir=frontend`
- [ ] `render.yaml` (SPEC §17.3): `runtime: image`, plano free, `autoDeploy: false`, `healthCheckPath: /health`, env vars
- [ ] `netlify.toml`: `publish = "frontend"`, sem build
- [ ] Netlify (manual): gerar `NETLIFY_AUTH_TOKEN`; criar projeto vazio sem Git via API (sem upload manual); anotar `NETLIFY_SITE_ID` (Project ID) e a URL
- [ ] GHCR (manual): tornar o pacote da imagem público após o primeiro push
- [ ] Render (manual): Blueprint a partir do repo; preencher `DATABASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `ALLOWED_ORIGINS` (URL do Netlify); anotar a `ADMIN_KEY` gerada; copiar o deploy hook
- [ ] GitHub (manual): secrets `RENDER_DEPLOY_HOOK_URL`, `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID` no ambiente `production`; variable `BACKEND_URL`
- [ ] Atualizar `API_BASE_URL` em `frontend/js/config.js` com a URL do Render

## Critérios de aceite
- [ ] Push na `main` com CI verde publica API e site sem passo manual
- [ ] Render e Netlify sem auto-deploy próprio (CT7)
- [ ] `https://<api>.onrender.com/health` → `status: ok`, `gemini_configured: true`
- [ ] Site do Netlify cadastra, busca e exclui em produção
- [ ] Restart manual do serviço no Render preserva o catálogo (CA10)

## Notas
- No primeiro run os jobs de deploy falham por falta de secrets (esperado); o push da imagem ao GHCR acontece antes. Ordem completa em SPEC §17.6.

## Referências
SPEC §17, D26
