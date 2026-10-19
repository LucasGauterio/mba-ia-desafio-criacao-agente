---
name: plan-resolve
description: Resolve interativamente as pendências listadas em validation.md de uma fase até o status virar clean, escrevendo o código/teste necessário ou documentando a limitação aceita.
---

# plan-resolve: Resolução de Pendências de Fase

## Objetivo
Para cada pendência marcada `[ ]` em `docs/phases/phase-NN-{slug}/validation.md`:
1. Se for fechável sem depender de uma chamada real ao LLM (ex.: função sem teste, endpoint sem caminho de sucesso testado) — escrever o teste/código que fecha a lacuna.
2. Se depender de comportamento real do modelo (roteamento `transfer_to_agent`, resposta de chat) e não houver `GEMINI_API_KEY`/`GOOGLE_API_KEY` configurada — **não simular um resultado que não provaria nada**. Registrar a limitação em `docs/decisions/technical-decisions-phase-NN-{slug}.md` com justificativa e apontar o caminho de verificação manual (ex. `TEST_PLAN.md`).

## Critério de Saída
Rodar `uv run pytest` com cobertura; toda pendência fechada deve corresponder a uma linha antes "Missing" agora executada, com 100% dos testes passando. Atualizar `validation.md` para `clean` somente quando toda pendência estiver fechada ou explicitamente aceita com justificativa documentada.
