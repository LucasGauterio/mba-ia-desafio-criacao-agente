# Fase 06: Execução Automatizada do TEST_PLAN.md

## Objetivo
Automatizar a execução e validação dos 18 casos de teste (CT-01 a CT-18) do [`TEST_PLAN.md`](../../../TEST_PLAN.md) contra a API real do Residencial Aurora com o LLM real (Gemini), incluindo o reinício real do processo (CT-13) e a disputa concorrente real (CT-14), sem nenhum mock.

Bibliotecas decididas nesta fase: ver [`library-refs.md`](library-refs.md).

## Mapa de Dependências
- Pré-requisitos: Fases 01-05 implementadas; `GOOGLE_API_KEY`/`GEMINI_API_KEY` configurada em `.env`; `uv sync` executado.
- Insumos: [`TEST_PLAN.md`](../../../TEST_PLAN.md) (fonte da verdade dos 18 casos de teste).

## Step Implementations (SIs)
1. **SI-06-01**: Criar [`scripts/run_test_plan.sh`](../../../scripts/run_test_plan.sh) cobrindo CT-01 a CT-18, com resolução de interpretador via `uv`/`.venv`, helpers de asserção e extração de JSON via Python, e ciclo de vida real da API (start/stop/restart). **Concluído.**
2. **SI-06-02**: Diagnosticar e corrigir a causa raiz dos erros em `POST /sessoes/{id}/mensagens` observados nas execuções reais. **Concluído**: `extrair_confirmacoes_pendentes` lia `args["payload"]` em vez do formato real `args["toolConfirmation"]["payload"]` — corrigido em [`src/aurora/api.py`](../../../src/aurora/api.py) e em [`tests/test_api_integration.py`](../../../tests/test_api_integration.py).
3. **SI-06-03**: Corrigir o bug do próprio script: `start_api()` reabria `api.log` com `>` (truncando) a cada reinício. **Concluído**: trunca uma única vez no início da execução, `>>` (append) em cada restart.
4. **SI-06-04**: Executar [`scripts/run_test_plan.sh`](../../../scripts/run_test_plan.sh) do início ao fim (CT-01 a CT-18) sem falhas contra a API real. **Parcialmente concluído** — uma execução completa real do usuário rodou os 18 CTs sem travar por rate limiting, mas revelou um bug real (`reservar_area` não resolvia o nome legível da área), já corrigido e validado isoladamente; falta reconfirmar a rodada completa 18/18 após a correção.
5. **SI-06-05**: Atualizar [`docs/TRACKER.md`](../../TRACKER.md) com a evidência de execução real (distinta da suíte mockada da Fase 05). **Pendente.**
6. **SI-06-06**: adicionar espera configurável entre chamadas em `scripts/run_test_plan.sh` para tornar a execução completa reprodutível independentemente da quota da chave. **Concluído**: `REQUEST_DELAY_SECONDS` (padrão 5s) aplicado antes de toda chamada a `/mensagens`/`/confirmacoes` (via `http()`) e antes do disparo concorrente do CT-14.

## Entregáveis e Critérios de Conclusão
- [x] Script `run_test_plan.sh` criado, com sintaxe válida (`bash -n`) e cobrindo os 18 CTs do `TEST_PLAN.md`.
- [x] CT-01 a CT-12 validados com sucesso contra a API real em pelo menos uma execução cada.
- [x] CT-13 (reinício real do processo) validado com sucesso: contagem de eventos preservada, dados de domínio intactos, e `POST /mensagens` voltou a funcionar após o restart — evidência real da Garantia 3.
- [x] CT-14 (disputa concorrente real) validado com sucesso após corrigir o `wait` sem argumentos do próprio script: uma sessão recebeu `sucesso` (código novo gerado), a outra `"já está ocupado"` — exatamente o comportamento esperado da Garantia 5 sob concorrência real.
- [x] Bug real de formato do ADK (`toolConfirmation.payload`) identificado, corrigido e coberto por teste mockado fiel ao formato real (31/31 testes da suíte continuam passando).
- [x] Bug real de resolução de área (`"salão de festas"` vs. `"salao-de-festas"`) identificado numa execução completa real, corrigido em `src/aurora/tools.py#_resolver_area`, e revalidado ao vivo isoladamente.
- [ ] **Pendência (SI-06-04)**: reconfirmar a execução completa 18/18 após a correção acima; rate limiting da API real continua um risco externo que pode interromper uma rodada.
