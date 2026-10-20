# Contexto da Fase 06: Execução Automatizada do TEST_PLAN.md

## Resumo Técnico
- `TEST_PLAN.md` define 18 casos de teste (CT-01 a CT-18, cobrindo os 15 Passos do avaliador + 3 cenários de borda complementares) a serem executados manualmente via `curl` contra a API real, com `GOOGLE_API_KEY`/`GEMINI_API_KEY` configurada.
- Esta fase automatiza esse roteiro inteiro em `scripts/run_test_plan.sh`, incluindo o reinício real do processo da API (CT-13) e a disputa concorrente real com dois `curl` simultâneos (CT-14) — nada é mockado.
- Decisões técnicas detalhadas em [`docs/decisions/technical-decisions-phase-06-test-plan-execution.md`](../../decisions/technical-decisions-phase-06-test-plan-execution.md).
- Esta fase depende das Fases 01-05 (API, agentes e tools já implementados) e é complementar à Fase 05: a Fase 05 prova as garantias com testes determinísticos e mockados; a Fase 06 prova o comportamento real do sistema fim-a-fim com o LLM de verdade.
- Primeira execução (2026-10-19) encontrou um bug real não coberto pela suíte mockada: `POST /mensagens` retorna `500` após a primeira chamada real ao Gemini no processo, até o próximo reinício. A causa raiz ainda não foi diagnosticada porque o próprio script trunca o log da API no restart do CT-13 (ver `docs/decisions/`).
