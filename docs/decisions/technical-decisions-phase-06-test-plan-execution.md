# Decisões Técnicas — Fase 06: Execução Automatizada do TEST_PLAN.md

## Script bash de automação em vez de um novo arquivo pytest
- **Alternativas consideradas**: adicionar os 18 casos de teste (CT-01 a CT-18) como mais um arquivo em `tests/`, ao lado de `test_evaluator_flow.py`.
- **Justificativa**: `TEST_PLAN.md` é, por definição (ver `docs/decisions/technical-decisions-phase-05-e2e-evaluator-validation.md`), o roteiro **manual/E2E contra o LLM real** — o oposto do que a suíte `pytest` decidiu ser (determinística, sem rede, sem chave de API). Misturar os dois violaria essa decisão já tomada na Fase 05. Um script `scripts/run_test_plan.sh` dedicado mantém a fronteira clara: `uv run pytest` nunca depende de `GEMINI_API_KEY`; `scripts/run_test_plan.sh` sempre depende.

## `curl` + Python inline (via `json_field`) em vez de `jq`
- **Alternativas consideradas**: `jq` para extração de campos JSON.
- **Justificativa**: `jq` não é uma dependência garantida no ambiente do avaliador/desenvolvedor; o projeto já depende de Python (via `uv`/`.venv`), então usar `python -c "import json..."` como extrator evita introduzir uma nova dependência externa de sistema.

## Resolução do interpretador via `uv run python -c "...sys.executable"` com fallback para `.venv/`
- **Alternativas consideradas**: assumir `python`/`python3` no `PATH`.
- **Justificativa**: o projeto é gerenciado exclusivamente por `uv` (`python-uv-conventions`); resolver o interpretador do ambiente correto (e não um Python global do sistema) evita rodar contra dependências desatualizadas ou ausentes.

## Reinício real do processo no CT-13 (kill + restart), sem simulação
- **Alternativas consideradas**: apenas recriar o objeto `Runner` em memória, sem matar o processo do SO.
- **Justificativa**: o Passo 13 do avaliador testa a Garantia 3 ("nada se perde no reinício") precisamente contra a hipótese de perda de estado em memória; simular o reinício sem matar o processo do SO não provaria nada sobre persistência real em disco. No Windows, a identificação do processo é feita por porta (`netstat` + `taskkill //PID ... //F`), não pelo PID do job do bash, que nem sempre corresponde ao processo nativo do Windows quando lançado via Git Bash.

## Achado em aberto: erro 500 intermitente em `POST /mensagens` com LLM real
- **Observação**: na primeira execução completa do script (2026-10-19), **todas** as chamadas a `POST /sessoes/{id}/mensagens` falharam com `500` a partir do CT-03 (primeira chamada real ao Gemini no processo), em sessões diferentes (`S1` e depois `S2`), até o reinício do CT-13 — após o qual todas as chamadas voltaram a responder `200` sem nenhuma mudança de código.
- **Hipótese de trabalho**: algum estado em memória do processo (não a sessão/banco, que sobreviveu ao restart normalmente) fica corrompido na primeira invocação real do `Runner`/Gemini e afeta todas as chamadas subsequentes até o processo ser reiniciado.
- **Status**: causa raiz **não identificada** — o traceback original foi perdido porque `start_api()` reabre `api.log` com `>` (truncando) no próprio restart do CT-13. Isso é, por si só, um bug do script de teste (SI-06-03) que precisa ser corrigido antes de poder diagnosticar o bug da aplicação (SI-06-02).
