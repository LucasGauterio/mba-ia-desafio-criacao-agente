# Contexto da Fase 06: Execução Automatizada do TEST_PLAN.md

## Resumo Técnico
- `TEST_PLAN.md` define 18 casos de teste (CT-01 a CT-18, cobrindo os 15 Passos do avaliador + 3 cenários de borda complementares) a serem executados manualmente via `curl` contra a API real, com `GOOGLE_API_KEY`/`GEMINI_API_KEY` configurada.
- Esta fase automatiza esse roteiro inteiro em `scripts/run_test_plan.sh`, incluindo o reinício real do processo da API (CT-13) e a disputa concorrente real com dois `curl` simultâneos (CT-14) — nada é mockado.
- Decisões técnicas detalhadas em [`docs/decisions/technical-decisions-phase-06-test-plan-execution.md`](../../decisions/technical-decisions-phase-06-test-plan-execution.md).
- Esta fase depende das Fases 01-05 (API, agentes e tools já implementados) e é complementar à Fase 05: a Fase 05 prova as garantias com testes determinísticos e mockados; a Fase 06 prova o comportamento real do sistema fim-a-fim com o LLM de verdade.
- Primeira execução (2026-10-19) encontrou falhas reais não cobertas pela suíte mockada. Causas raiz diagnosticadas e corrigidas: (1) `extrair_confirmacoes_pendentes` lia o formato errado do payload do ADK (`src/aurora/api.py`); (2) `reservar_area`/`verificar_disponibilidade_area` não resolviam o nome legível da área (`src/aurora/tools.py#_resolver_area`); (3) rate limiting/quota da chave Gemini sob chamadas em sequência rápida, mitigado com `REQUEST_DELAY_SECONDS`; (4) bug de seleção de confirmação por índice `[0]` no próprio script. Ver `docs/decisions/` para o histórico completo. Execução final: 90/90 passos OK, 0 FALHOU.
