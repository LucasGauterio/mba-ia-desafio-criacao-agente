# Validação Arquitetural da Fase 06

- **Status**: `dirty`
- **Validação de Conformidade**:
  - [x] `scripts/run_test_plan.sh` existe, é sintaticamente válido (`bash -n`) e cobre os 18 CTs de `TEST_PLAN.md`.
  - [x] Os 4 artefatos obrigatórios da fase existem: `CONTEXT.md`, `validation.md`, `library-refs.md`, `phase-06-test-plan-execution.md`.
  - [x] CT-01, CT-02 e CT-09 passam contra a API real.
  - [x] CT-13 (reinício real do processo, Garantia 3) passa contra a API real — evidência mais forte que a suíte mockada da Fase 05, que não reinicia um processo de verdade.
- **Pendências para fechar `clean`** (ver detalhamento em [`docs/decisions/technical-decisions-phase-06-test-plan-execution.md`](../../decisions/technical-decisions-phase-06-test-plan-execution.md)):
  - [ ] **SI-06-03**: `start_api()` trunca `api.log` a cada restart (`>` em vez de modo que preserve o log anterior); corrigir antes de poder diagnosticar qualquer outro bug encontrado em execução.
  - [ ] **SI-06-02**: causa raiz do `500` em `POST /sessoes/{id}/mensagens` não identificada — ocorreu de forma consistente do CT-03 ao CT-12 (e em uma segunda sessão no CT-10) na primeira execução real, e desapareceu após o reinício do CT-13 sem qualquer mudança de código. Hipótese de trabalho: estado em memória do processo corrompido na primeira chamada real ao `Runner`/Gemini.
  - [ ] **SI-06-04**: execução completa e bem-sucedida dos 18 CTs ainda não alcançada — a última execução foi abortada pelo usuário durante o CT-14 (disputa concorrente), em 2026-10-19.
  - [ ] **SI-06-05**: `docs/TRACKER.md` ainda não referencia a execução real desta fase (só referencia a suíte mockada da Fase 05).

## Como reproduzir / continuar
1. Corrigir SI-06-03 (log em modo append, ou um arquivo de log por instância).
2. Reproduzir o `500` isoladamente: subir a API em foreground com `python -u` (sem buffer) e repetir a mensagem exata do CT-03 (`"Sou do apartamento 302. Quais reservas e quais visitantes o 302 tem?"`) na sessão recém-criada, para capturar o traceback real.
3. Corrigir a causa raiz identificada (SI-06-02).
4. Rodar `scripts/run_test_plan.sh` do início ao fim e confirmar `0 FALHOU` no resumo final.
5. Atualizar este arquivo para `clean` e `docs/TRACKER.md` (SI-06-05).
