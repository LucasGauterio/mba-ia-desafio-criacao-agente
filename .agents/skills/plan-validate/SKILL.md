---
name: plan-validate
description: Audita uma fase contra o código e os testes reais (não contra a documentação) e escreve docs/phases/phase-NN-{slug}/validation.md com status clean ou dirty e pendências nomeadas.
---

# plan-validate: Validação Arquitetural de Fase

## Objetivo
Confrontar os artefatos de planejamento (`CONTEXT.md`, `phase-NN-{slug}.md`) com a implementação real, nunca confiar apenas na documentação:
1. Rodar a suíte de testes com cobertura (`uv run pytest`, que já usa `--cov=aurora --cov-report=term-missing` via `pyproject.toml`).
2. Localizar funções declaradas como entregues nos Step Implementations mas cujas linhas aparecem em "Missing" no relatório de cobertura — elas foram importadas em teste mas nunca chamadas, ou nunca sequer importadas.
3. Confirmar que cada critério de entrega do `phase-NN-{slug}.md` é verificável apontando para um teste ou comando real (link `arquivo#Lnn`).

## Arquivo Gerado
`docs/phases/phase-NN-{slug}/validation.md`:
- `Status: clean` — todas as pendências fechadas ou explicitamente aceitas como limitação documentada.
- `Status: dirty` — lista nomeada de pendências, cada uma com referência a arquivo e linha/função.

## Regra
Nunca marcar `clean` com uma pendência conhecida sem uma entrada correspondente em `docs/decisions/technical-decisions-phase-NN-{slug}.md` explicando por que é uma limitação aceita (ex.: comportamento de LLM não testável sem `GEMINI_API_KEY`/`GOOGLE_API_KEY`) — do contrário, é um gap sem explicação e o status deve ser `dirty`.
