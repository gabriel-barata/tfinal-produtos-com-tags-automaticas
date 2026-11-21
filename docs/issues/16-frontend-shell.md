# 16 · Frontend: estrutura base, cliente da API e status do servidor

| Campo | Valor |
|---|---|
| Labels | `frontend` |
| Tamanho | M |
| Depende de | 03 |
| Branch | `feat/16-frontend-shell` |

## Objetivo
Página única com layout, Pico.css, módulo de API e banner de cold start.

## Escopo
- [ ] `frontend/index.html`: layout da SPEC §12.5 (header, coluna de cadastro, coluna de busca/resultados, rodapé), Pico.css via CDN com versão fixada, `<script type="module" src="js/main.js">`
- [ ] `frontend/css/styles.css`: ajustes finos (grid responsivo, chips, destaque de tag)
- [ ] `js/config.js` (SPEC §12.3)
- [ ] `js/api.js`: funções da SPEC §12.4, `AbortController` 90 s, `ApiError`, 422 → texto legível
- [ ] `js/components/server-status.js`: banner após 2 s sem resposta do `/health`; botão "tentar de novo" em erro
- [ ] `js/main.js`: monta os componentes (os demais entram nos cards 17–19)

## Critérios de aceite
- [ ] Abre em `localhost:8080` via compose sem erros no console
- [ ] Com API parada: banner de erro + "tentar de novo"
- [ ] Layout empilha corretamente em largura de celular

## Referências
SPEC §12
