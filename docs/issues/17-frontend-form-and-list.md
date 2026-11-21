# 17 · Frontend: cadastro e lista de produtos

| Campo | Valor |
|---|---|
| Labels | `frontend` |
| Tamanho | M |
| Depende de | 15, 16 |
| Branch | `feat/17-frontend-form-and-list` |

## Objetivo
Cadastrar produto e ver o catálogo em cards.

## Escopo
- [ ] `js/components/product-form.js`: validação de tamanho no cliente, estado "IA gerando tags…", exibe produto criado com tags, mensagens de erro do `ApiError`, callback `onCreated`
- [ ] `js/components/product-list.js`: grid de cards (nome, descrição truncada ~140, tags), destaque das `matched_tags`, estado vazio, função `render(results, { canDelete })`
- [ ] `main.js`: ao criar, recarrega a lista

## Critérios de aceite
- [ ] Cadastro ponta a ponta no ambiente Docker mostra as tags geradas pelo Gemini
- [ ] 503 mostra "Serviço de IA indisponível, tente novamente."
- [ ] Lista inicial = todos os produtos, mais recentes primeiro

## Referências
SPEC §12.5, CA1, CA5
