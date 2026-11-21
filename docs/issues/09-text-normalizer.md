# 09 · Normalização de tags e de busca

| Campo | Valor |
|---|---|
| Labels | `backend` |
| Tamanho | P |
| Depende de | 07 |
| Branch | `feat/09-text-normalizer` |

## Objetivo
Uma única pipeline de normalização usada para tags geradas e para termos de busca.

## Escopo
- [ ] `app/utils/text_normalizer.py`: `normalize_tag(raw) -> tuple[str, ...]`, `normalize_tags(raws) -> tuple[str, ...]` (dedupe com `HashSet`, preservando ordem), `tokenize_query(query) -> tuple[str, ...]`
- [ ] Pipeline: lower/strip → remove acentos (NFKD) → não `[a-z0-9]` vira espaço → quebra em palavras → remove stopwords (`de, da, do, das, dos, para, com, em, e, a, o, as, os, um, uma`) → descarta < 2 ou > 30 caracteres
- [ ] Testes parametrizados

## Critérios de aceite
- [ ] `"Calçado Esportivo"` → `("calcado", "esportivo")`
- [ ] `"tênis de corrida"` → `("tenis", "corrida")`
- [ ] `"  AZUL!! "` → `("azul",)`
- [ ] `normalize_tags(["azul", "Azul", "azul escuro"])` → `("azul", "escuro")`
- [ ] `tokenize_query("para")` → `()`

## Referências
SPEC §6.3
