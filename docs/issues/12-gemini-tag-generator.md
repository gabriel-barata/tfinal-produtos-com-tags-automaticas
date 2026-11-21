# 12 · `GeminiTagGenerator`

| Campo | Valor |
|---|---|
| Labels | `ia`, `backend` |
| Tamanho | M |
| Depende de | 08, 09 |
| Branch | `feat/12-gemini-tag-generator` |

## Objetivo
Gerar tags com Gemini usando structured output, validar, normalizar e aplicar retry.

## Escopo
- [ ] `TagGenerationError` em `app/exceptions.py`
- [ ] `app/services/tag_generator.py`:
  - [ ] `build_response_schema()` gerado a partir de `BASE_VOCABULARY` (enums + min/max)
  - [ ] `build_prompt(name, description, existing_free_tags)` → (system instruction, conteúdo), conforme SPEC §7.3
  - [ ] Modelo Pydantic privado `_GeneratedTags` para revalidação
  - [ ] `GeminiTagGenerator(client, model, max_attempts=2, timeout_s=15).generate(name, description, existing_free_tags) -> tuple[str, ...]`
  - [ ] Pós-processamento SPEC §7.4 (ordem dos grupos, `normalize_tags`, máx. 4 livres)
  - [ ] Temperatura 0,2
- [ ] Testes com client mockado (sem rede): sucesso, JSON inválido → retry → sucesso, 2 falhas → `TagGenerationError`, truncamento de livres, schema contém os 31 enums
- [ ] Definir o valor padrão de `GEMINI_MODEL` conferindo no AI Studio o Flash vigente no free tier

## Critérios de aceite
- [ ] Exemplo da SPEC §7.5 produz exatamente as tags finais esperadas (com resposta mockada)
- [ ] `existing_free_tags` aparece no prompt; vazio no primeiro cadastro
- [ ] Nenhuma chamada de rede nos testes

## Referências
SPEC §7
