---
name: research
description: Investiga e documenta as decisões técnicas/arquiteturais de uma fase antes do planejamento formal, gerando docs/decisions/technical-decisions-{slug}.md.
---

# research: Descoberta de Decisões Técnicas

## Objetivo
Documentar, para uma fase específica (`phase-NN`), as decisões arquiteturais já tomadas ou a tomar. Isto não é sobre bibliotecas — isso é papel do `library-refs.md` gerado por `/plan-build` — mas sobre escolhas de abordagem: estratégia de concorrência, isolamento de estado, estratégia de teste, trade-offs aceitos e suas alternativas descartadas.

## Arquivo Gerado
`docs/decisions/technical-decisions-phase-NN-{slug}.md`, com uma entrada por decisão:
- **Decisão**: o que foi escolhido.
- **Alternativas consideradas**: o que foi descartado e por quê.
- **Justificativa**: trade-off que motivou a escolha.
- **ADR relacionada**: link para `docs/adrs/ADR-*.md` quando a decisão já tiver uma ADR formal.
- **Limitação conhecida** (quando houver): ex. uma decisão de teste que não cobre comportamento real do LLM por falta de `GEMINI_API_KEY`/`GOOGLE_API_KEY` no ambiente.

## Quando Usar
Antes de `/plan-context NN`, sempre que a fase introduzir uma escolha arquitetural nova, ou para auditar/justificar retroativamente uma decisão já implementada.
