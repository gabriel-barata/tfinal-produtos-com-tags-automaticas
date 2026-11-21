# 19 · Frontend: chave admin e exclusão

| Campo | Valor |
|---|---|
| Labels | `frontend` |
| Tamanho | P |
| Depende de | 17 |
| Branch | `feat/19-frontend-admin-delete` |

## Objetivo
Permitir excluir produtos informando a chave de administrador.

## Escopo
- [ ] `js/components/admin-panel.js`: campo de senha + salvar; `localStorage` com try/catch; callback `onKeyChange`
- [ ] Botão "excluir" nos cards só com chave salva; `confirm()` antes de excluir
- [ ] 401 → apaga a chave salva e avisa; 204 → recarrega lista e filtros

## Critérios de aceite
- [ ] Sem chave: nenhum botão excluir visível
- [ ] Chave errada: aviso + chave removida
- [ ] Chave certa: produto some da lista e tags exclusivas somem dos filtros (CA8)

## Referências
SPEC §12.5, §14, CA8, CA9
