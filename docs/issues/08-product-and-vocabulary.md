# 08 · Entidade `Product` + vocabulário de tags

| Campo | Valor |
|---|---|
| Labels | `backend` |
| Tamanho | P |
| Depende de | 02 |
| Branch | `feat/08-product-and-vocabulary` |

## Objetivo
Modelos de domínio: o produto e as 31 tags base agrupadas.

## Escopo
- [ ] `app/models/product.py`: `@dataclass(frozen=True) Product(id, name, description, tags: tuple[str, ...], created_at)`
- [ ] `app/models/tag_vocabulary.py`: `TagGroup(StrEnum)` com `DEPARTMENT, SPORTS, AUDIENCE, COLORS, FREE`; `BASE_VOCABULARY` (valores da SPEC §6.2, como `tuple`); `group_of(tag) -> TagGroup`
- [ ] Constantes de cardinalidade por grupo (min/max) reutilizáveis pelo schema do Gemini
- [ ] Testes

## Critérios de aceite
- [ ] 31 tags base, nenhuma repetida entre grupos
- [ ] `group_of("corrida") == SPORTS`, `group_of("tenis") == FREE`
- [ ] `raquete` presente em `sports`; `tenis` ausente do vocabulário base

## Referências
SPEC §6.1, §6.2
