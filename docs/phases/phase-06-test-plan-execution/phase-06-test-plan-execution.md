# Fase 06: Execução Automatizada do TEST_PLAN.md

## Objetivo
Automatizar a execução e validação dos 18 casos de teste (CT-01 a CT-18) do [`TEST_PLAN.md`](../../../TEST_PLAN.md) contra a API real do Residencial Aurora com o LLM real (Gemini), incluindo o reinício real do processo (CT-13) e a disputa concorrente real (CT-14), sem nenhum mock.

Bibliotecas decididas nesta fase: ver [`library-refs.md`](library-refs.md).

## Mapa de Dependências
- Pré-requisitos: Fases 01-05 implementadas; `GOOGLE_API_KEY`/`GEMINI_API_KEY` configurada em `.env`; `uv sync` executado.
- Insumos: [`TEST_PLAN.md`](../../../TEST_PLAN.md) (fonte da verdade dos 18 casos de teste).

## Step Implementations (SIs)
1. **SI-06-01**: Criar [`scripts/run_test_plan.sh`](../../../scripts/run_test_plan.sh) cobrindo CT-01 a CT-18, com resolução de interpretador via `uv`/`.venv`, helpers de asserção e extração de JSON via Python, e ciclo de vida real da API (start/stop/restart). **Concluído.**
2. **SI-06-02**: Diagnosticar e corrigir a causa raiz dos erros `500` em `POST /sessoes/{id}/mensagens` observados na primeira execução real (a partir do CT-03, até o reinício do CT-13). **Pendente.**
3. **SI-06-03**: Corrigir o bug do próprio script: `start_api()` reabre `api.log` com `>` (truncando) a cada reinício, destruindo o traceback da instância anterior — necessário para poder diagnosticar o SI-06-02. **Pendente.**
4. **SI-06-04**: Executar [`scripts/run_test_plan.sh`](../../../scripts/run_test_plan.sh) do início ao fim (CT-01 a CT-18) sem falhas contra a API real. **Pendente** (execução abortada pelo usuário durante o CT-14, antes da correção do SI-06-02/03).
5. **SI-06-05**: Atualizar [`docs/TRACKER.md`](../../TRACKER.md) com a evidência de execução real (distinta da suíte mockada da Fase 05) após o SI-06-04 ter sucesso. **Pendente.**

## Entregáveis e Critérios de Conclusão
- [x] Script `run_test_plan.sh` criado, com sintaxe válida (`bash -n`) e cobrindo os 18 CTs do `TEST_PLAN.md`.
- [x] CT-01, CT-02 e CT-09 validados com sucesso contra a API real (sem LLM necessário para a lógica desses três).
- [x] CT-13 (reinício real do processo) validado com sucesso: contagem de eventos preservada, dados de domínio intactos, e `POST /mensagens` voltou a funcionar após o restart — evidência real da Garantia 3.
- [ ] **Pendência (SI-06-02)**: causa raiz do `500` em `POST /mensagens` (CT-03 a CT-12, e CT-10 em S2) não identificada.
- [ ] **Pendência (SI-06-03)**: truncamento do log da API a cada restart impede diagnosticar o SI-06-02.
- [ ] **Pendência (SI-06-04)**: execução completa e bem-sucedida dos 18 CTs ainda não alcançada (abortada no CT-14 pelo usuário, em 2026-10-19, antes da correção acima).
