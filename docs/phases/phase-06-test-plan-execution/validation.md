# Validação Arquitetural da Fase 06

- **Status**: `dirty`
- **Validação de Conformidade**:
  - [x] `scripts/run_test_plan.sh` existe, é sintaticamente válido (`bash -n`) e cobre os 18 CTs de `TEST_PLAN.md`.
  - [x] Os 4 artefatos obrigatórios da fase existem: `CONTEXT.md`, `validation.md`, `library-refs.md`, `phase-06-test-plan-execution.md`.
  - [x] **SI-06-02 concluído**: causa raiz do bug de `confirmacoes_pendentes` com `acao`/`detalhes` vazios identificada e corrigida — `src/aurora/api.py#extrair_confirmacoes_pendentes` lia `args["payload"]`; o formato real do ADK é `args["toolConfirmation"]["payload"]`. Corrigido, e `tests/test_api_integration.py` atualizado para mockar o formato real (os 31 testes da suíte mockada continuam passando).
  - [x] **SI-06-03 concluído**: `start_api()` agora faz append a `api.log` (truncado uma única vez no início da execução), preservando o log através de reinícios — permitiu diagnosticar o SI-06-02.
  - [x] Bug adicional encontrado e corrigido: `ct14()` usava `wait` sem argumentos, que esperava indefinidamente o processo da própria API (também iniciado com `&` no mesmo shell) em vez de só os dois `curl` concorrentes. Corrigido para `wait "$pid_s3" "$pid_s4"`.
  - [x] CT-01 a CT-14 validados com sucesso contra a API real em pelo menos uma execução cada (ver `docs/decisions/technical-decisions-phase-06-test-plan-execution.md` para o histórico), incluindo CT-13 (reinício real do processo, Garantia 3) e CT-14 (disputa concorrente real: uma sessão recebeu `sucesso`, a outra `já está ocupado`, exatamente como esperado).
- **Pendências para fechar `clean`**:
  - [ ] **SI-06-04**: execução completa e limpa dos 18 CTs em uma única rodada ainda não alcançada. A tentativa mais recente travou a partir do CT-07 por **rate limiting/quota da API do Gemini** na chave configurada (`POST /mensagens` parou de responder dentro do timeout de 60s, sem exceção no servidor) — uma restrição externa do ambiente, não um bug de código. Ver `docs/decisions/` para os sintomas observados.
  - [ ] **Melhoria recomendada (SI-06-06, não crítica)**: adicionar um intervalo de espera configurável entre chamadas em `scripts/run_test_plan.sh` (ou documentar o requisito de uma chave com quota maior) para tornar a execução completa reprodutível independentemente da quota da chave do executor.
  - [ ] **SI-06-05**: `docs/TRACKER.md` ainda não referencia `scripts/run_test_plan.sh` como evidência de execução real complementar à suíte mockada da Fase 05.

## Como reproduzir / continuar
1. Confirmar que a `GOOGLE_API_KEY`/`GEMINI_API_KEY` configurada tem quota suficiente para ~18 sequências de chamadas (ou aguardar a janela de limite de taxa resetar entre tentativas).
2. Rodar `scripts/run_test_plan.sh` do início ao fim e confirmar `0 FALHOU` no resumo final.
3. Se o rate limiting persistir, implementar o SI-06-06 (espera entre chamadas) antes de insistir.
4. Atualizar este arquivo para `clean` e `docs/TRACKER.md` (SI-06-05) após uma execução 18/18 limpa.
