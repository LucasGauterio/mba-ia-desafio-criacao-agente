# Validação Arquitetural da Fase 06

- **Status**: `clean`
- **Validação de Conformidade**:
  - [x] `scripts/run_test_plan.sh` existe, é sintaticamente válido (`bash -n`) e cobre os 18 CTs de `TEST_PLAN.md`.
  - [x] Os 4 artefatos obrigatórios da fase existem: `CONTEXT.md`, `validation.md`, `library-refs.md`, `phase-06-test-plan-execution.md`.
  - [x] **SI-06-02 concluído**: causa raiz do bug de `confirmacoes_pendentes` com `acao`/`detalhes` vazios identificada e corrigida — `src/aurora/api.py#extrair_confirmacoes_pendentes` lia `args["payload"]`; o formato real do ADK é `args["toolConfirmation"]["payload"]`. Corrigido, e `tests/test_api_integration.py` atualizado para mockar o formato real.
  - [x] **SI-06-03 concluído**: `start_api()` faz append a `api.log` (truncado uma única vez no início da execução), preservando o log através de reinícios.
  - [x] Bug adicional corrigido: `ct14()` usava `wait` sem argumentos, que esperava indefinidamente o processo da própria API em vez de só os dois `curl` concorrentes. Corrigido para `wait "$pid_s3" "$pid_s4"`.
  - [x] Bug real corrigido: `reservar_area`/`verificar_disponibilidade_area` não resolviam o nome legível da área ("salão de festas") que o Gemini naturalmente passa, só o slug exato ("salao-de-festas"). Corrigido com `_resolver_area()` em `src/aurora/tools.py`, cobertura adicionada em `tests/test_tools.py`.
  - [x] **SI-06-06 concluído**: `REQUEST_DELAY_SECONDS` (padrão 5s, ajustável/desligável via env var) aplicado antes de toda chamada que aciona o LLM real.
  - [x] Bug corrigido no próprio script: `confirmacoes_pendentes[0]` assumia que a confirmação mais relevante estava no índice 0, mas o agente pode legitimamente retomar um pedido anterior não resolvido e devolver mais de uma confirmação pendente na mesma resposta. `confirmacao_campo()` agora seleciona pela `acao` esperada (`ct07`, `ct08`, `ct11`). CT-13 ajustado para verificar o total de reservas condicionalmente ao que o CT-08 de fato concluiu nessa execução.
  - [x] **SI-06-04 concluído**: execução completa e limpa de `scripts/run_test_plan.sh` contra a API real — **90/90 passos OK, 0 FALHOU** (2026-10-20), incluindo CT-13 (reinício real, Garantia 3) e CT-14 (disputa concorrente real, Garantia 5).
  - [x] **SI-06-05 concluído**: `docs/TRACKER.md` referencia `scripts/run_test_plan.sh` como evidência de execução real complementar à suíte mockada.

## Histórico de diagnóstico
Ver [`docs/decisions/technical-decisions-phase-06-test-plan-execution.md`](../../decisions/technical-decisions-phase-06-test-plan-execution.md) para o relato completo de cada bug encontrado e corrigido ao longo das execuções reais (API do ADK, resolução de área, script de teste).
